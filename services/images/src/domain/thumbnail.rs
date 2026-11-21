//! Thumbnails made from photos.

use crate::domain::size::{Fitting, Size, Unfit};

/// Why a thumbnail cannot be made.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum Refused {
    /// The payload is not a picture the service reads.
    #[error("the payload is not a picture: {0}")]
    Broken(String),
    /// The wanted size makes no thumbnail.
    #[error(transparent)]
    Unfit(#[from] Unfit),
}

/// Decoded picture that can be drawn at another size.
pub trait Picture {
    /// Returns the size of the picture.
    fn size(&self) -> Size;
    /// Returns the picture drawn at the size and encoded.
    fn drawn(&self, size: Size) -> Result<Vec<u8>, Refused>;
}

/// Codec that reads pictures from bytes.
pub trait Codec {
    /// Picture the codec reads.
    type Decoded: Picture;
    /// Returns the picture in the bytes, or why it cannot be read.
    fn decoded(&self, bytes: &[u8]) -> Result<Self::Decoded, Refused>;
}

/// Encoded thumbnail with its size.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Thumbnail {
    /// Encoded image.
    image: Vec<u8>,
    /// Size of the image.
    size: Size,
}

impl Thumbnail {
    /// Creates a thumbnail.
    #[must_use]
    pub const fn new(image: Vec<u8>, size: Size) -> Self {
        Self { image, size }
    }
}

/// Parts of a thumbnail.
pub trait Made {
    /// Returns the encoded image.
    fn image(&self) -> &[u8];
    /// Returns the size of the image.
    fn size(&self) -> Size;
}

impl Made for Thumbnail {
    fn image(&self) -> &[u8] {
        &self.image
    }

    fn size(&self) -> Size {
        self.size
    }
}

/// Source of thumbnails.
pub trait Thumbnailed {
    /// Returns the thumbnail of the photo in the bytes, fitted to the width.
    fn thumbnail(&self, bytes: &[u8], width: u32) -> Result<Thumbnail, Refused>;
}

/// Thumbnails drawn with a codec.
#[derive(Debug, Clone, Copy)]
pub struct Thumbnails<C> {
    /// Codec that reads and writes the pictures.
    codec: C,
}

impl<C> Thumbnails<C> {
    /// Creates thumbnails drawn with the codec.
    #[must_use]
    pub const fn new(codec: C) -> Self {
        Self { codec }
    }
}

impl<C: Codec> Thumbnailed for Thumbnails<C> {
    fn thumbnail(&self, bytes: &[u8], width: u32) -> Result<Thumbnail, Refused> {
        let picture = self.codec.decoded(bytes)?;
        let size = picture.size().fitted(width.max(1))?;
        Ok(Thumbnail::new(Vec::new(), size))
    }
}

#[cfg(test)]
mod tests {
    use super::{Codec, Made, Picture, Refused, Thumbnail, Thumbnailed, Thumbnails};
    use crate::domain::size::{Sides, Size, Unfit};

    struct Blank {
        size: Size,
    }

    impl Picture for Blank {
        fn size(&self) -> Size {
            self.size
        }

        fn drawn(&self, size: Size) -> Result<Vec<u8>, Refused> {
            Ok(format!("{}x{}", size.width(), size.height()).into_bytes())
        }
    }

    struct Text;

    impl Codec for Text {
        type Decoded = Blank;

        fn decoded(&self, bytes: &[u8]) -> Result<Blank, Refused> {
            let text = String::from_utf8_lossy(bytes);
            let (width, height) = text
                .split_once('x')
                .ok_or_else(|| Refused::Broken(text.to_string()))?;
            Ok(Blank {
                size: Size::new(width.parse().unwrap(), height.parse().unwrap()),
            })
        }
    }

    #[test]
    fn draws_the_photo_at_the_fitted_size() {
        let made = Thumbnails::new(Text).thumbnail(b"800x600", 400).unwrap();
        assert_eq!(
            made,
            Thumbnail::new(b"400x300".to_vec(), Size::new(400, 300))
        );
        assert_eq!(made.image(), b"400x300");
        assert_eq!(made.size(), Size::new(400, 300));
    }

    #[test]
    fn refuses_a_broken_payload() {
        assert_eq!(
            Thumbnails::new(Text).thumbnail(b"garbage", 400),
            Err(Refused::Broken(String::from("garbage")))
        );
    }

    #[test]
    fn refuses_a_zero_width() {
        assert_eq!(
            Thumbnails::new(Text).thumbnail(b"800x600", 0),
            Err(Refused::Unfit(Unfit::ZeroWidth))
        );
    }
}
