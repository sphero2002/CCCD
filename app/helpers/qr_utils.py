# app/helpers/qr_utils.py
from typing import Union, Tuple, Dict
import cv2
import numpy as np
from pyzbar.pyzbar import decode as decodeQR, ZBarSymbol
from scipy import ndimage
from math import ceil, floor

# Define constants
BBOX_XYXY = 'bbox_xyxy'
BBOX_XYXYN = f'{BBOX_XYXY}n'
CXCY = 'cxcy'
CXCYN = f'{CXCY}n'
WH = 'wh'
WHN = f'{WH}n'
POLYGON_XY = 'polygon_xy'
POLYGON_XYN = f'{POLYGON_XY}n'
PADDED_QUAD_XY = 'padded_quad_xy'
PADDED_QUAD_XYN = f'{PADDED_QUAD_XY}n'
QUAD_XY = 'quad_xy'
QUAD_XYN = f'{QUAD_XY}n'
IMAGE_SHAPE = 'image_shape'

_SHARPEN_KERNEL = np.array(
    ((-1.0, -1.0, -1.0), (-1.0, 9.0, -1.0), (-1.0, -1.0, -1.0)), dtype=np.float32
)

class QRHelper:
    def wrap(self, scale_factor: float, corrections: str, flavor: str, blur_kernel_sizes: Tuple[Tuple[int, int], ...], image: np.ndarray, results: list) -> list:
        """
        Wraps the decoding results with additional information such as scaling, flavor, and image adjustments.
        
        :param scale_factor: The scaling factor applied to the image.
        :param corrections: The type of correction applied (e.g., 'cropped_bbox', 'corrected_perspective').
        :param flavor: The type of image (e.g., 'original', 'inverted', 'grayscale').
        :param blur_kernel_sizes: The kernel sizes used for blurring.
        :param image: The processed image.
        :param results: The decoded QR codes in zbar format.
        :return: A list containing the wrapped results.
        """
        return [
            {
                "scale_factor": scale_factor,
                "corrections": corrections,
                "flavor": flavor,
                "blur_kernel_sizes": blur_kernel_sizes,
                "image": image,
                "results": results
            }
        ]
    
    def _decode_qr_zbar_v2(self, image: np.ndarray, detection_result: Dict[str, Union[np.ndarray, float, Tuple[float, int]]]) -> list:
        """
        Try to decode the QR code just with pyzbar, pre-processing the image in various ways 
        to improve detection and decoding rates.

        :param image: np.ndarray. The image to be read. It must be a np.ndarray (HxWxC) (uint8).
        :param detection_result: dict. The detection result, which contains bounding box or quadrilateral information.
        :return: list. A list of decoded QR codes in the zbar format, or an empty list if no QR code is detected.
        """
        # Extract the bounding box or quadrilateral for cropping
        cropped_bbox, _ = self.crop_qr(image=image, detection=detection_result, crop_key=BBOX_XYXY)
        cropped_quad, updated_detection = self.crop_qr(image=image, detection=detection_result, crop_key=PADDED_QUAD_XY)

        # Correct perspective if needed
        corrected_perspective = self.__correct_perspective(image=cropped_quad, padded_quad_xy=updated_detection[PADDED_QUAD_XY])

        # Try different scale factors and preprocess the image for decoding
        for scale_factor in (1, 0.5, 2, 0.25, 3, 4):
            for label, img in {
                "cropped_bbox": cropped_bbox,
                "corrected_perspective": corrected_perspective,
            }.items():
                # Skip rescaling if image dimensions exceed 1024px
                if not all(25 < axis < 1024 for axis in img.shape[:2]) and scale_factor != 1:
                    continue

                # Rescale the image
                rescaled_image = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
                decodedQR = decodeQR(image=rescaled_image, symbols=[ZBarSymbol.QRCODE])
                
                # Check if decoding was successful
                if len(decodedQR) > 0:
                    return self.wrap(scale_factor=scale_factor, corrections=label, flavor="original", blur_kernel_sizes=None,
                                     image=rescaled_image, results=decodedQR)

                # Try inverting the image for black-background-white-text QR codes
                inverted_image = 255 - rescaled_image
                decodedQR = decodeQR(image=inverted_image, symbols=[ZBarSymbol.QRCODE])
                if len(decodedQR) > 0:
                    return self.wrap(scale_factor=scale_factor, corrections=label, flavor="inverted", blur_kernel_sizes=None,
                                     image=inverted_image, results=decodedQR)

                # Convert to grayscale if image is not already in grayscale
                if len(rescaled_image.shape) == 3:
                    gray = cv2.cvtColor(rescaled_image, cv2.COLOR_BGR2GRAY)
                else:
                    gray = rescaled_image

                # Try decoding with blurred grayscale image
                decodedQR = self.__threshold_and_blur_decodings(image=gray, blur_kernel_sizes=((5, 5), (7, 7)))
                if len(decodedQR) > 0:
                    return self.wrap(scale_factor=scale_factor, corrections=label, flavor="grayscale", blur_kernel_sizes=((5, 5), (7, 7)),
                                     image=gray, results=decodedQR)

                # Sharpen the image if previous steps failed
                sharpened_image = cv2.filter2D(rescaled_image, -1, _SHARPEN_KERNEL)
                decodedQR = self.__threshold_and_blur_decodings(image=sharpened_image, blur_kernel_sizes=((3, 3),))
                if len(decodedQR) > 0:
                    return self.wrap(scale_factor=scale_factor, corrections=label, flavor="sharpened", blur_kernel_sizes=((3, 3),),
                                     image=sharpened_image, results=decodedQR)

        return []
    
    def __threshold_and_blur_decodings(self, image: np.ndarray, blur_kernel_sizes: Tuple[Tuple[int, int]]) -> list:
        """
        Applies different blur and threshold filters to an image before decoding.

        :param image: np.ndarray. The image to be processed.
        :param blur_kernel_sizes: tuple. Kernel sizes for blur filters.
        :return: list. The decoded QR codes in zbar format.
        """
        decodedQR = decodeQR(image=image, symbols=[ZBarSymbol.QRCODE])
        if decodedQR:
            return decodedQR

        # Binarize image if it's 2D
        if len(image.shape) == 2:
            _, binary_image = cv2.threshold(image, thresh=0, maxval=255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            decodedQR = decodeQR(image=binary_image, symbols=[ZBarSymbol.QRCODE])
            if decodedQR:
                return decodedQR

        # Apply different blur kernels
        for kernel_size in blur_kernel_sizes:
            blur_image = cv2.GaussianBlur(image, kernel_size, 0)
            decodedQR = decodeQR(image=blur_image, symbols=[ZBarSymbol.QRCODE])
            if decodedQR:
                return decodedQR
        return []

    def __correct_perspective(self, image: np.ndarray, padded_quad_xy: np.ndarray) -> np.ndarray:
        """
        Corrects the perspective of a QR code based on the provided quadrilateral coordinates.

        :param image: np.ndarray. The image to be corrected.
        :param padded_quad_xy: np.ndarray. The quadrilateral points for perspective correction.
        :return: np.ndarray. The perspective-corrected image.
        """
        # Ensure that padded_quad_xy is of type np.float32
        padded_quad_xy = np.array(padded_quad_xy, dtype=np.float32)

        # Compute width and height for the quadrilateral
        width1 = np.sqrt(((padded_quad_xy[0][0] - padded_quad_xy[1][0]) ** 2) + ((padded_quad_xy[0][1] - padded_quad_xy[1][1]) ** 2))
        width2 = np.sqrt(((padded_quad_xy[2][0] - padded_quad_xy[3][0]) ** 2) + ((padded_quad_xy[2][1] - padded_quad_xy[3][1]) ** 2))

        height1 = np.sqrt(((padded_quad_xy[0][0] - padded_quad_xy[3][0]) ** 2) + ((padded_quad_xy[0][1] - padded_quad_xy[3][1]) ** 2))
        height2 = np.sqrt(((padded_quad_xy[1][0] - padded_quad_xy[2][0]) ** 2) + ((padded_quad_xy[1][1] - padded_quad_xy[2][1]) ** 2))

        # Use maximum width and height
        max_width = max(int(width1), int(width2))
        max_height = max(int(height1), int(height2))

        # Create destination points for perspective transform
        dst_pts = np.array([[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]], dtype=np.float32)

        # Get perspective transform matrix and apply
        M = cv2.getPerspectiveTransform(padded_quad_xy, dst_pts)
        dst_img = cv2.warpPerspective(image, M, (max_width, max_height))

        return dst_img
    
    def crop_qr(self, image: np.ndarray, detection: Dict[str, Union[np.ndarray, float, Tuple[float, int]]], crop_key: str = BBOX_XYXY) -> Tuple[np.ndarray, Dict[str, Union[np.ndarray, float, Tuple[float, int]]]]:
        """
        Crop the QR code from the image.
        :param image: np.ndarray. The image to crop the QR code from.
        :param detection: dict[str, np.ndarray|float|tuple[float|int, float|int]]. The detection of the QR code returned
                        by QRDetector.detect(). Take into account that this method will return a tuple of detections,
                            and this function only expects one of them.
        :param crop_key: str. The key of the detection to use to crop the QR code. It can be one of the following:
                        'bbox_xyxy', 'bbox_xyn', 'quad_xy', 'quad_xyn', 'padded_quad_xy', 'padded_quad_xyn',
                        'polygon_xy' or 'polygon_xyn'..
        :return: tuple[np.ndarray, dict[str, np.ndarray|float|tuple[float|int, float|int]]]. The cropped QR code, and the
                        updated detection to fit the cropped image.
        """
        if crop_key in (BBOX_XYXYN, QUAD_XYN, PADDED_QUAD_XYN, POLYGON_XYN):
            # If it is normalized, transform it to absolute coordinates.
            crop_key = crop_key[:-1]

        # Get the surrounding box of the QR code
        if crop_key == BBOX_XYXY:
            x1, y1, x2, y2 = detection[crop_key]
        else:
            (x1, y1), (x2, y2) = detection[crop_key].min(axis=0), detection[crop_key].max(axis=0)
        x1, y1, x2, y2 = floor(x1), floor(y1), ceil(x2), ceil(y2)

        # Apply padding if needed
        h, w = image.shape[:2]
        left_pad, top_pad = max(0, -x1), max(0, -y1)
        right_pad, bottom_pad = max(0, x2 - w), max(0, y2 - h)

        if any(pad > 0 for pad in (left_pad, top_pad, right_pad, bottom_pad)):
            white = 255 if image.dtype == np.uint8 else 1.
            if len(image.shape) == 3:
                image = np.pad(image, ((top_pad, bottom_pad), (left_pad, right_pad), (0, 0)), mode='constant',
                               constant_values=white)
            else:
                image = np.pad(image, ((top_pad, bottom_pad), (left_pad, right_pad)), mode='constant',
                               constant_values=white)
            h, w = image.shape[:2]
            x1, y1, x2, y2 = x1 + left_pad, y1 + top_pad, x2 + left_pad, y2 + top_pad
        image = image[y1:y2, x1:x2].copy()

        # Recalculate detection for cropped image
        detection.update({
            BBOX_XYXY: np.array([0., 0., w, h], dtype=np.float32),
            CXCY: (w / 2., h / 2.),
            WH: (w, h),
            POLYGON_XY: detection[POLYGON_XY] - (x1, y1),
            QUAD_XY: detection[QUAD_XY] - (x1, y1),
            PADDED_QUAD_XY: detection[PADDED_QUAD_XY] - (x1, y1),
            IMAGE_SHAPE: (h, w),
        })

        return image, detection
