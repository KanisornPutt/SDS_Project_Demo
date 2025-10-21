import express from "express";
import bodyParser from "body-parser";
import { marked } from "marked";

const app = express();
app.use(bodyParser.text({ type: "*/*" }));

app.post("/parse", (req, res) => {
    try {
        const markdown = req.body || "";
        // marked should handle newlines correctly by default
        const html = marked(markdown);
        res.json({ html });
    } catch (error) {
        console.error("Parse error:", error);
        res.status(500).json({ error: "Failed to parse markdown" });
    }
});

app.listen(8081, () => console.log("✅ md-parser running on :8081"));