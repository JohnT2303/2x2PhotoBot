document.addEventListener("DOMContentLoaded", () => {
    const imageUploader = document.getElementById("imageUploader");
    const saveButton = document.getElementById("saveImage");
    const originalImage = document.getElementById("originalImage");
    const processedImage = document.getElementById("processedImage");

    let originalImageData = null;

    imageUploader.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                originalImageData = e.target.result;
                originalImage.src = originalImageData;
            };
            reader.readAsDataURL(file);
        }
    });


    saveButton.addEventListener("click", () => {
        if (!processedImage.src) {
            alert("No processed image to save!");
            return;
        }

        const a = document.createElement("a");
        a.href = processedImage.src;
        a.download = "processed_image.jpg";
        a.click();
    });






});
