import { useState } from "react";
import "./App.css";

export default function App() {
  const [result, setResult] = useState();
  const [question, setQuestion] = useState();
  const [file, setFile] = useState();
  const [isSubmitting, setIsSubmitting] = useState(false); // Added state to track form submission

  const handleQuestionChange = (event: any) => {
    setQuestion(event.target.value);
  };

  const handleFileChange = (event: any) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = (event: any) => {
    event.preventDefault();
    setIsSubmitting(true); // Set form as submitting

    const formData = new FormData();

    if (file) {
      formData.append("file", file);
    }

    const fileApiUrl = `${window.location.origin}/api/file`;
    console.log("fileApiUrl", fileApiUrl);

    fetch(fileApiUrl, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        const pdfName = data.filename;
        console.log("filename", pdfName);

        const predictApiUrl = `${window.location.origin}/api/predict`;
        return fetch(predictApiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
            Origin: window.location.origin,
            Pragma: "no-cache",
            Referer: window.location.origin,
            "User-Agent": navigator.userAgent,
          },
          body: JSON.stringify({
            question: question,
            pdf_name: pdfName,
          }),
        });
      })
      .then((response) => response.json())
      .then((data) => {
        setResult(data.result);
      })
      .catch((error) => {
        console.error("Error during API calls", error);
      })
      .finally(() => {
        setIsSubmitting(false); // Reset form submission state
      });
  };

  return (
    <div className="appBlock">
      <form onSubmit={handleSubmit} className="form">
        <label className="questionLabel" htmlFor="question">
          Question:
        </label>

        <input
          className="questionInput"
          id="question"
          type="text"
          value={question}
          onChange={handleQuestionChange}
          placeholder="Ask your question here"
        />
        <br />
        <label className="fileLabel" htmlFor="file">
          Upload PDF file:
        </label>

        <input type="file" id="file" name="file" accept=".pdf" onChange={handleFileChange} className="fileInput" />
        <br />
<button
  className={`submitBtn ${isSubmitting ? 'submitBtnSubmitting' : ''}`}
  type="submit"
  disabled={!file || !question || isSubmitting}
>
  {isSubmitting ? <div className="spinner"></div> : "Submit"}
</button>
      </form>
      <p className="resultOutput">Result: {result}</p>
    </div>
  );
}

