import React from "react";

const ProductTable = ({ products }) => {
  console.log("Products:", products); 
    
  const renderOptions = (options) => {
    return Object.entries(options || {}).map(([key, values], index) => (
      <div key={index}>
        <strong>{key.charAt(0).toUpperCase() + key.slice(1)}:</strong> 
        {Array.isArray(values) ? values.join(", ") : "No options available"}
      </div>
    ));
  };
  
  const renderImages = (images = []) => {
    return (
      <div className="image-gallery">
        {images.map((image, index) => (
          <img
            key={index}
            src={image}
            alt={`${index + 1}`}
            className="product-image"
          />
        ))}
      </div>
    );
  };
  
  const renderVideos = (videos) => {
    if (!videos || videos.length === 0) {
      return "No Videos";
    }
  
    return videos.map((video, videoIndex) => (
      <div key={videoIndex} style={{marginBottom: "20px"}}>
        <a href={video} target="_blank" rel="noopener noreferrer">
          Video {videoIndex + 1}
        </a>
      </div>
    ));
  };
  
  const renderRatingDistribution = (distribution) => {
    return Object.entries(distribution || {}).map(([rating, percentage], index) => (
      <div key={index}>
        <strong>{rating}:</strong> {percentage}
      </div>
    ));
  };

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Created At</th>
            <th>Image</th>
            <th>Name</th>
            <th>Price</th>
            <th>Rating</th>
            <th>Total Ratings</th>
            <th>Rating Distribution</th>
            <th>Options</th>
            <th>Specifications</th>
            <th>Features</th>
            <th>Secondary Images</th>
            <th>Featured Images</th>
            <th>Videos</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {products.length > 0 ? (
            products.map((product, index) => (
              <tr key={index}>
                <td>{product.created_at || "N/A"}</td>
                <td>
                    <img
                        src={product.media?.primary_image}
                        alt={product.name}
                        style={{ maxWidth: "200px", width: "auto" }}
                    />
                </td>
                <td>{product.name || "No Name"}</td>
                <td className="ratings">{product.price || "N/A"}</td>
                <td className="ratings">{product.ratings?.avg_rating || "No Ratings"}</td>
                <td className="ratings">{product.ratings?.total_ratings || "No Ratings"}</td>
                <td>
                  {renderRatingDistribution(product.ratings?.distribution)}
                </td>
                <td>
                  {renderOptions(product.options)}
                </td>
                <td>
                  {Object.entries(product.specifications || {}).slice(0, 30).map(([key, value]) => (
                    <div key={key}><b>{key}:</b> {value}</div>
                  ))}
                </td>
                <td>
                  <ul>
                    {product.features?.slice(0, 3).map((feature, i) => (
                      <li key={i}>{feature}</li>
                    ))}
                  </ul>
                </td>
                <td>
                  {renderImages(product.media?.secondary_images)}
                </td>
                <td>
                  {renderImages(product.media?.featured_images)}
                </td>
                <td>
                  {product.media?.videos ? (
                    renderVideos(product.media?.videos)
                  ) : (
                    "No Videos"
                  )}
                </td>
                <td>
                    <button 
                        onClick={() => window.open(product.url, "_blank")}
                        className="view-button"
                    >
                        View
                    </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="11">No products available</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ProductTable;
