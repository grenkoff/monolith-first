//! gRPC endpoint of the images service.

use std::sync::Arc;

use contracts::images::v1::images_service_server::ImagesService;
use contracts::images::v1::{ThumbnailRequest, ThumbnailResponse};
use tonic::{Request, Response, Status};

use crate::domain::size::Sides;
use crate::domain::thumbnail::{Made, Thumbnailed};

/// Adapter: answers the thumbnail requests of core over gRPC.
#[derive(Debug)]
pub struct Endpoint<T> {
    /// Source of the thumbnails.
    thumbnails: Arc<T>,
}

impl<T> Endpoint<T> {
    /// Creates the endpoint that draws with the thumbnails.
    #[must_use]
    pub const fn new(thumbnails: Arc<T>) -> Self {
        Self { thumbnails }
    }
}

#[tonic::async_trait]
impl<T: Thumbnailed + Send + Sync + 'static> ImagesService for Endpoint<T> {
    async fn thumbnail(
        &self,
        request: Request<ThumbnailRequest>,
    ) -> Result<Response<ThumbnailResponse>, Status> {
        let message = request.into_inner();
        let thumbnails = Arc::clone(&self.thumbnails);
        let made = tokio::task::spawn_blocking(move || {
            thumbnails.thumbnail(&message.image, message.width)
        })
        .await
        .map_err(|error| Status::internal(error.to_string()))?
        .map_err(|refused| Status::invalid_argument(refused.to_string()))?;
        let size = made.size();
        Ok(Response::new(ThumbnailResponse {
            image: made.image().to_vec(),
            width: size.width(),
            height: size.height(),
        }))
    }
}

#[cfg(test)]
mod tests {
    use std::io::Cursor;
    use std::sync::Arc;

    use contracts::images::v1::ThumbnailRequest;
    use contracts::images::v1::images_service_server::ImagesService;
    use image::{ImageFormat, Rgb, RgbImage};
    use tonic::{Code, Request};

    use super::Endpoint;
    use crate::domain::thumbnail::Thumbnails;
    use crate::infra::codec::Bitmap;

    fn endpoint() -> Endpoint<Thumbnails<Bitmap>> {
        Endpoint::new(Arc::new(Thumbnails::new(Bitmap)))
    }

    fn png() -> Vec<u8> {
        let mut bytes = Vec::new();
        RgbImage::from_pixel(80, 60, Rgb([30, 200, 30]))
            .write_to(&mut Cursor::new(&mut bytes), ImageFormat::Png)
            .unwrap();
        bytes
    }

    #[tokio::test]
    async fn answers_a_thumbnail_that_fits_the_width() {
        let answer = endpoint()
            .thumbnail(Request::new(ThumbnailRequest {
                image: png(),
                width: 40,
            }))
            .await
            .unwrap()
            .into_inner();
        assert_eq!((answer.width, answer.height), (40, 30));
        assert_eq!(
            image::guess_format(&answer.image).unwrap(),
            ImageFormat::Jpeg
        );
    }

    #[tokio::test]
    async fn refuses_a_payload_that_is_no_picture() {
        let status = endpoint()
            .thumbnail(Request::new(ThumbnailRequest {
                image: b"garbage".to_vec(),
                width: 40,
            }))
            .await
            .unwrap_err();
        assert_eq!(status.code(), Code::InvalidArgument);
    }

    #[tokio::test]
    async fn refuses_a_zero_width() {
        let status = endpoint()
            .thumbnail(Request::new(ThumbnailRequest {
                image: png(),
                width: 0,
            }))
            .await
            .unwrap_err();
        assert_eq!(status.code(), Code::InvalidArgument);
    }
}
