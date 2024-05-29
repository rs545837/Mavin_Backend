# Project Overview: Research Report Automation on WhatsApp

## Introduction

Welcome to the Research Report Automation project! This project aims to simplify and automate the process of generating comprehensive research reports based on user queries through WhatsApp. By leveraging the capabilities of various sub-agents and orchestration models, the system provides detailed, accurate, and user-friendly research reports in PDF format, delivered directly to users on WhatsApp.

## Features

- **Automated Research Reports**: Users can ask questions through WhatsApp, and the system generates detailed research reports in response.
- **PDF Generation**: The final output is provided in a well-structured PDF format, making it easy to read and share.
- **Text and Audio Processing**: The system can process both text and audio inputs to generate comprehensive reports.
- **Multilingual Support**: Reports can be generated in different languages, including Hindi and Hinglish (Hindi written in Roman script).
- **Cloud Integration**: The project utilizes cloud services for storing and sharing the generated PDFs, ensuring easy access and distribution.

## How It Works

1. **User Query**: The user sends a question or request via WhatsApp.
2. **Text Extraction**: The system extracts relevant text from various sources, including PDFs and other documents.
3. **Audio Generation**: If needed, the text can be converted into audio using advanced speech synthesis models.
4. **Translation**: The extracted text can be translated into different languages as required by the user.
5. **Orchestration and Sub-Agent Processing**: The main orchestrator divides the task into smaller subtasks, which are handled by specialized sub-agents. Each sub-agent processes its assigned task and returns the result.
6. **Refinement**: The results from the sub-agents are combined and refined to create a cohesive and comprehensive final output.
7. **PDF Creation**: The refined content is formatted into a PDF file.
8. **Delivery**: The PDF is uploaded to a cloud storage service, and a link to the PDF is sent back to the user via WhatsApp.

## Components

### Text Extraction

- **PDF Text Extraction**: The system can extract text from PDF files, ensuring that all relevant information is captured accurately.

### Audio Generation

- **Text-to-Speech**: Converts the extracted text into high-quality audio using state-of-the-art speech synthesis models.

### Translation

- **Language Translation**: Supports translation of text into multiple languages, including Hindi and Hinglish.

### Orchestration

- **Task Division**: The main orchestrator breaks down the user's query into smaller, manageable tasks.
- **Sub-Agent Processing**: Each sub-agent specializes in a specific aspect of the task, ensuring efficient and accurate processing.

### Refinement

- **Content Refinement**: Combines and refines the results from the sub-agents to create a final, polished report.

### PDF Generation

- **Markdown to PDF**: Converts the refined content into a well-structured PDF file.
- **Cloud Storage**: Uploads the PDF to a cloud storage service for easy access and sharing.

### WhatsApp Integration

- **Query Handling**: Receives user queries via WhatsApp.
- **Response Delivery**: Sends the link to the generated PDF back to the user on WhatsApp.

## Usage

1. **Send a Query**: Start by sending your research question or request to the designated WhatsApp number.
2. **Wait for Processing**: The system will process your query, extract relevant information, and generate a report.
3. **Receive PDF**: You will receive a link to the generated PDF report on WhatsApp.

## Future Enhancements

- **Enhanced Audio Features**: Incorporate more advanced audio processing capabilities.
- **Additional Language Support**: Expand the range of supported languages.
- **Improved Orchestration**: Optimize the orchestration process for faster and more accurate report generation.

## Conclusion

This project aims to streamline the process of generating detailed research reports by leveraging advanced text and audio processing techniques, multilingual support, and seamless integration with WhatsApp. We hope this tool enhances your research capabilities and makes information more accessible and easier to share.
