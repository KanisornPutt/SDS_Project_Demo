const express = require("express");
const multer = require("multer");
const axios = require("axios");
const cors = require("cors");
const FormData = require("form-data");

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors());

const IPYNB_SERVICE = process.env.IPYNB_SERVICE || "http://localhost:5000";
const PDF_SERVICE = process.env.PDF_SERVICE || "http://localhost:8080";

app.post("/convert", upload.single("file"), async (req, res) => {
  try {
    console.log("Received file:", req.file.originalname);

    // Step 1: Convert IPYNB to HTML
    const formData1 = new FormData();
    formData1.append("file", req.file.buffer, req.file.originalname);

    const htmlResponse = await axios.post(
      `${IPYNB_SERVICE}/convert`,
      formData1,
      {
        headers: formData1.getHeaders(),
        responseType: "text",
      }
    );

    console.log("Got HTML from service 3");

    // Step 2: Convert HTML to PDF
    const formData2 = new FormData();
    formData2.append("html", htmlResponse.data);

    const pdfResponse = await axios.post(`${PDF_SERVICE}/convert`, formData2, {
      headers: formData2.getHeaders(),
      responseType: "arraybuffer",
    });

    console.log("Got PDF from service 4");

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", "attachment; filename=output.pdf");
    res.send(Buffer.from(pdfResponse.data));
  } catch (error) {
    console.error("Gateway error:", error.message);
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚪 API Gateway running on port ${PORT}`);
});
