//! Pictures read and written with the `image` crate.

use image::DynamicImage;
use image::codecs::jpeg::JpegEncoder;
use image::imageops::FilterType;

use crate::domain::size::{Sides, Size};
use crate::domain::thumbnail::{Codec, Picture, Refused};

/// Quality of the JPEG thumbnails, from 1 to 100.
const QUALITY: u8 = 85;

/// Adapter: codec of JPEG, PNG and WebP photos from the `image` crate.
#[derive(Debug, Clone, Copy, Default)]
pub struct Bitmap;

/// Photo decoded by the `image` crate.
pub struct Decoded {
    /// Pixels of the photo.
    image: DynamicImage,
}

impl Codec for Bitmap {
    type Decoded = Decoded;

    fn decoded(&self, bytes: &[u8]) -> Result<Decoded, Refused> {
        image::load_from_memory(bytes)
            .map(|image| Decoded { image })
            .map_err(|error| Refused::Broken(error.to_string()))
    }
}

impl Picture for Decoded {
    fn size(&self) -> Size {
        Size::new(self.image.width(), self.image.height())
    }

    fn drawn(&self, size: Size) -> Result<Vec<u8>, Refused> {
        let resized = self
            .image
            .resize_exact(size.width(), size.height(), FilterType::Lanczos3)
            .to_rgb8();
        let mut bytes = Vec::new();
        JpegEncoder::new_with_quality(&mut bytes, QUALITY)
            .encode_image(&resized)
            .map_err(|error| Refused::Broken(error.to_string()))?;
        Ok(bytes)
    }
}

#[cfg(test)]
mod tests {
    use std::io::Cursor;

    use image::{ImageFormat, Rgb, RgbImage};

    use super::Bitmap;
    use crate::domain::size::Size;
    use crate::domain::thumbnail::{Codec, Picture, Refused};

    fn png(width: u32, height: u32) -> Vec<u8> {
        let mut bytes = Vec::new();
        RgbImage::from_pixel(width, height, Rgb([200, 30, 30]))
            .write_to(&mut Cursor::new(&mut bytes), ImageFormat::Png)
            .unwrap();
        bytes
    }

    #[test]
    fn reads_the_size_of_a_png() {
        assert_eq!(
            Bitmap.decoded(&png(40, 20)).unwrap().size(),
            Size::new(40, 20)
        );
    }

    #[test]
    fn draws_a_jpeg_of_the_given_size() {
        let drawn = Bitmap
            .decoded(&png(40, 20))
            .unwrap()
            .drawn(Size::new(10, 5))
            .unwrap();
        assert_eq!(image::guess_format(&drawn).unwrap(), ImageFormat::Jpeg);
        let reread = image::load_from_memory(&drawn).unwrap();
        assert_eq!((reread.width(), reread.height()), (10, 5));
    }

    #[test]
    fn refuses_bytes_that_are_no_picture() {
        assert!(matches!(
            Bitmap.decoded(b"not a picture"),
            Err(Refused::Broken(_))
        ));
    }
}
