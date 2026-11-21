//! Entry point of the images service.

use std::sync::Arc;

use contracts::images::v1::images_service_server::ImagesServiceServer;
use images::api::endpoint::Endpoint;
use images::api::health::{Health, Routes};
use images::domain::thumbnail::Thumbnails;
use images::infra::codec::Bitmap;
use images::infra::setting::{Env, Setting};

/// Largest photo accepted in one request, in bytes.
const MESSAGE_LIMIT: usize = 16 * 1024 * 1024;

/// Composition root: wires the images service and serves gRPC and health checks.
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .json()
        .with_env_filter(tracing_subscriber::EnvFilter::new(
            Env::new("RUST_LOG", "info").value(),
        ))
        .init();
    let grpc = Env::new("IMAGES_GRPC_ADDR", "0.0.0.0:50051")
        .value()
        .parse()?;
    let http =
        tokio::net::TcpListener::bind(Env::new("IMAGES_HTTP_ADDR", "0.0.0.0:8080").value()).await?;
    tracing::info!(%grpc, http = %http.local_addr()?, "images is starting");
    let stop = || async {
        if let Err(error) = tokio::signal::ctrl_c().await {
            tracing::error!(%error, "cannot listen for the shutdown signal");
        }
    };
    tokio::try_join!(
        async {
            tonic::transport::Server::builder()
                .add_service(
                    ImagesServiceServer::new(Endpoint::new(Arc::new(Thumbnails::new(Bitmap))))
                        .max_decoding_message_size(MESSAGE_LIMIT),
                )
                .serve_with_shutdown(grpc, stop())
                .await
                .map_err(anyhow::Error::from)
        },
        async {
            axum::serve(http, Health.router())
                .with_graceful_shutdown(stop())
                .await
                .map_err(anyhow::Error::from)
        },
    )?;
    Ok(())
}
