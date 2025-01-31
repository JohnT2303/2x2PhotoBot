import React, { useState } from "react";
import axios from "axios";

const IDPhotoProcessor = () => {
    const [selectedImage, setSelectedImage] = useState(null);
    const [brightness, setBrightness] = useState(1.0);
    const [filters, setFilters] = useState({
        grayscale: false,
        sepia: false,
    });
    const [processedImage, setProcessedImage] = useState(null);

    const handleImageUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => setSelectedImage(reader.result);
            reader.readAsDataURL(file);
        }
    };

    const handleProcessImage = async () => {
        if (!selectedImage) {
            alert("Please upload an image first!");
            return;
        }

        try {
            const response = await axios.post("http://localhost:5000/process_image", {
                image: selectedImage,
                brightness: brightness,
                filters: filters,
            });

            setProcessedImage(response.data.processed_image);
        } catch (error) {
            console.error("Error processing image:", error);
            alert("Something went wrong while processing the image.");
        }
    };

    return (
        <div className="p-4 max-w-lg mx-auto">
            <h1 className="text-2xl font-bold mb-4">ID Photo Processor</h1>

            {/* Subir Imagen */}
            <div className="mb-4">
                <label className="block font-medium mb-2">Upload an Image:</label>
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="border p-2 w-full"
                />
            </div>

            {/* Ajustar Brillo */}
            <div className="mb-4">
                <label className="block font-medium mb-2">Adjust Brightness:</label>
                <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={brightness}
                    onChange={(e) => setBrightness(e.target.value)}
                    className="w-full"
                />
            </div>

            {/* Filtros */}
            <div className="mb-4">
                <label className="block font-medium mb-2">Filters:</label>
                <div className="flex gap-4">
                    <label>
                        <input
                            type="checkbox"
                            checked={filters.grayscale}
                            onChange={() =>
                                setFilters((prev) => ({ ...prev, grayscale: !prev.grayscale }))
                            }
                        />
                        Grayscale
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            checked={filters.sepia}
                            onChange={() =>
                                setFilters((prev) => ({ ...prev, sepia: !prev.sepia }))
                            }
                        />
                        Sepia
                    </label>
                </div>
            </div>

            {/* Botón para procesar */}
            <button
                onClick={handleProcessImage}
                className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
            >
                Process Image
            </button>

            {/* Mostrar resultados */}
            {processedImage && (
                <div className="mt-4">
                    <h2 className="text-xl font-medium mb-2">Processed Image:</h2>
                    <img
                        src={processedImage}
                        alt="Processed"
                        className="w-full border rounded"
                    />
                </div>
            )}
        </div>
    );
};

export default IDPhotoProcessor;
