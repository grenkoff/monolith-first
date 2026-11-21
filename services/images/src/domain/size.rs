//! Size of a picture in pixels and how it fits a width.

/// Why a picture cannot be fitted.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum Unfit {
    /// The wanted width is zero.
    #[error("the width of a thumbnail must be at least one pixel")]
    ZeroWidth,
}

/// Picture size that can shrink to a width.
pub trait Fitting {
    /// Returns the size that fits the width, keeping the proportions and never enlarging.
    fn fitted(&self, width: u32) -> Result<Size, Unfit>;
}

/// Width and height of a picture in pixels.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Size {
    /// Width in pixels.
    width: u32,
    /// Height in pixels.
    height: u32,
}

impl Size {
    /// Creates a size.
    #[must_use]
    pub const fn new(width: u32, height: u32) -> Self {
        Self { width, height }
    }
}

/// Two sides of a size.
pub trait Sides {
    /// Returns the width in pixels.
    fn width(&self) -> u32;
    /// Returns the height in pixels.
    fn height(&self) -> u32;
}

impl Sides for Size {
    fn width(&self) -> u32 {
        self.width
    }

    fn height(&self) -> u32 {
        self.height
    }
}

impl Fitting for Size {
    fn fitted(&self, width: u32) -> Result<Size, Unfit> {
        if width == 0 {
            return Err(Unfit::ZeroWidth);
        }
        if width >= self.width {
            return Ok(*self);
        }
        let scaled = (u64::from(self.height) * u64::from(width) * 2 + u64::from(self.width))
            / (u64::from(self.width) * 2);
        let height = u32::try_from(scaled)
            .unwrap_or(self.height)
            .min(self.height)
            .max(1);
        Ok(Self::new(width, height))
    }
}

#[cfg(test)]
mod tests {
    use super::{Fitting, Size, Unfit};

    #[test]
    fn shrinks_to_the_width_keeping_proportions() {
        assert_eq!(Size::new(4000, 3000).fitted(400), Ok(Size::new(400, 300)));
    }

    #[test]
    fn never_enlarges_a_small_picture() {
        assert_eq!(Size::new(200, 100).fitted(400), Ok(Size::new(200, 100)));
    }

    #[test]
    fn keeps_a_picture_of_the_same_width() {
        assert_eq!(Size::new(400, 100).fitted(400), Ok(Size::new(400, 100)));
    }

    #[test]
    fn rounds_the_height_to_the_nearest_pixel() {
        assert_eq!(Size::new(1000, 333).fitted(100), Ok(Size::new(100, 33)));
        assert_eq!(Size::new(1000, 335).fitted(100), Ok(Size::new(100, 34)));
    }

    #[test]
    fn keeps_at_least_one_pixel_of_height() {
        assert_eq!(Size::new(4000, 3).fitted(100), Ok(Size::new(100, 1)));
    }

    #[test]
    fn refuses_a_zero_width() {
        assert_eq!(Size::new(400, 300).fitted(0), Err(Unfit::ZeroWidth));
    }
}
