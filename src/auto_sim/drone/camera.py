from typing import Optional, Sequence, Tuple

import numpy as np
from isaacsim.sensors.camera import Camera as IsaacCamera
from numpy.typing import NDArray
from pxr import Sdf


def distort_ray_kannala_brandt(
    distortion_model: Sequence[float],
    theta: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Distort a ray using the Kannala-Brandt distortion model. For a given angle the
    corresponding distorted angle is calculated.
    """
    t3 = theta**3
    t5 = t3 * theta**2
    t7 = t5 * theta**2
    t9 = t7 * theta**2
    k1, k2, k3, k4 = list(distortion_model[:4])
    return theta + k1 * t3 + k2 * t5 + k3 * t7 + k4 * t9


def undistort_ray_kannala_brandt(
    backwards_distortion_model: Sequence[float],
    theta_d: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Undistort a ray using the Kannala-Brandt distortion model. For a given distorted
    angle the corresponding undistorted angle is calculated.
    """
    return np.polyval(np.array(backwards_distortion_model[::-1]), theta_d)


def calculate_backwards_distortion_model(
    distortion_model: Sequence[float],
    max_fov: float,
    n_points: int = 100,
    degree: int = 4,
) -> Sequence[float]:
    """The KB distortion model is a list of coefficients of a polynomial relating the
    distorted angle with the actual angle. This function will approximate the inverse
    function with a polynomial fit.

    r = f * d(theta) with d(theta) = theta * (1 + k1* theta^2 + k2 * theta^4 + ...)
    d^-1(theta_d) = j0 + j1 * theta + j2 * theta^2 + ...
    theta = d^-1(r/f)
    """

    # Create ranges of angles, concentrated near zero
    p = np.linspace(0, 1, n_points)
    theta = p**1.2 * max_fov / 2

    # Get the corresponding distorted angles
    theta_d = distort_ray_kannala_brandt(distortion_model, theta)

    # Find the best fit, going through the origin
    x = np.vstack([theta_d**i for i in range(1, degree + 1)]).T

    backwards_distortion_model, _, _, _ = np.linalg.lstsq(x, theta, rcond=None)

    return np.append(0, backwards_distortion_model).tolist()


class Camera(IsaacCamera):
    def __init__(
        self,
        prim_path: str,
        name: str = "camera",
        frequency: Optional[int] = None,
        dt: Optional[float] = None,
        resolution: Optional[Tuple[int, int]] = None,
        position: Optional[NDArray[np.float32]] = None,
        orientation: Optional[NDArray[np.float32]] = None,
        translation: Optional[NDArray[np.float32]] = None,
        render_product_path: Optional[str] = None,
    ) -> None:

        # Initialise the Isaac Sim Camera
        super().__init__(
            prim_path,
            name,
            frequency,
            dt,
            resolution,
            position,
            orientation,
            translation,
            render_product_path,
        )

    def set_kannala_brandt_properties(
        self,
        nominal_width: float,
        nominal_height: float,
        optical_centre_x: float,
        optical_centre_y: float,
        max_fov: float,
        distortion_model: Sequence[float],
    ) -> None:
        """Approximates kannala brandt distortion with ftheta fisheye polynomial \n
        coefficients.
        Args:
            nominal_width (float): Rendered Width (pixels)
            nominal_height (float): Rendered Height (pixels)
            optical_centre_x (float): Horizontal Render Position (pixels)
            optical_centre_y (float): Vertical Render Position (pixels)
            max_fov (Optional[float]): maximum field of view (pixels)
            distortion_model (Sequence[float]): kannala brandt generic distortion \n
        model coefficients (k1, k2, k3, k4)
        """

        backwards_distortion_model = calculate_backwards_distortion_model(
            distortion_model,
            max_fov=np.deg2rad(max_fov),
            n_points=int(nominal_width),
            degree=4,
        )

        fx = nominal_width * self.get_focal_length() / self.get_horizontal_aperture()
        fy = nominal_height * self.get_focal_length() / self.get_vertical_aperture()
        focal_length = (fx + fy) / 2

        for i, coefficient in enumerate(backwards_distortion_model):
            # Adjust coefficient for focal length.
            self.prim.CreateAttribute(
                "fthetaPoly" + (chr(ord("A") + i)), Sdf.ValueTypeNames.Float, False
            ).Set(float(coefficient * focal_length**-i))

        self.prim.CreateAttribute("fthetaWidth", Sdf.ValueTypeNames.Float, False).Set(
            nominal_width
        )
        self.prim.CreateAttribute("fthetaHeight", Sdf.ValueTypeNames.Float, False).Set(
            nominal_height
        )
        self.prim.CreateAttribute("fthetaCx", Sdf.ValueTypeNames.Float, False).Set(
            optical_centre_x
        )
        self.prim.CreateAttribute("fthetaCy", Sdf.ValueTypeNames.Float, False).Set(
            optical_centre_y
        )

        if max_fov:
            self.prim.CreateAttribute(
                "fthetaMaxFov", Sdf.ValueTypeNames.Float, False
            ).Set(max_fov)

        # Store the original distortion model parameters
        self.prim.CreateAttribute(
            "physicalDistortionModel", Sdf.ValueTypeNames.String
        ).Set("kannalaBrandt")
        self.prim.CreateAttribute(
            "physicalDistortionCoefficients", Sdf.ValueTypeNames.FloatArray, False
        ).Set(distortion_model)
