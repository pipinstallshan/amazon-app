import React, { useEffect, useState } from "react";
import ProductTable from "./components/ProductTable";
import "./styles.css";

const jsonFiles = [
  "/crawler/headphones.json",
  "/crawler/laptops.json",
  "/crawler/smartphones.json",
];

const App = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await Promise.all(
          jsonFiles.map(file =>
            fetch(file).then(res => res.json())
          )
        );
        setProducts(data.flat());
        setLoading(false);
      } catch (error) {
        console.error("Error loading JSON files:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="container">
      <h1>Product Listings</h1>
      {loading ? (
        <div className="spinner">Loading...</div>
      ) : (
        <ProductTable products={products} />
      )}
    </div>
  );
};

export default App;
