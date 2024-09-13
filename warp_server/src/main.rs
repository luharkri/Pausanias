use warp::Filter;

#[tokio::main]
async fn main() {
    // Create a basic route
    let hello = warp::path::end()
        .map(|| warp::reply::html("Hello, Rust Web Server!"));

    // Start the warp server
    warp::serve(hello)
        .run(([127, 0, 0, 1], 3030))
        .await;
}
