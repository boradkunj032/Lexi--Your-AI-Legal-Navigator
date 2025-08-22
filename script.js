document.addEventListener('DOMContentLoaded', () => {
    const docUploader = document.getElementById('docUploader');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const summaryOutput = document.getElementById('summaryOutput');
    const outputLangSelector = document.getElementById('outputLang');
    
    // Create a new Showdown converter
    const converter = new showdown.Converter();

    summarizeBtn.addEventListener('click', async () => {
        const file = docUploader.files[0];
        if (!file) {
            alert("Please select a document first!");
            return;
        }

        const outputLanguage = outputLangSelector.value;

        const formData = new FormData();
        formData.append('document', file);
        formData.append('output_language', outputLanguage);

        summaryOutput.innerHTML = "Analyzing your document... please wait."; // Use innerHTML here too

        try {
            const response = await fetch('http://127.0.0.1:5000/summarize', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                // Convert the Markdown summary to HTML
                const htmlSummary = converter.makeHtml(result.summary);
                // Use .innerHTML to render the formatted text
                summaryOutput.innerHTML = htmlSummary;
            } else {
                summaryOutput.innerText = `Error: ${result.error}`;
            }
        } catch (error) {
            console.error('Failed to connect to the server:', error);
            summaryOutput.innerText = 'Failed to connect to the server. Make sure it is running.';
        }
    });
});