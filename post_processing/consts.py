NEW_PAPERS_PATH =  "./experiments/concats/new_papers.csv"
# # NEW_PAPERS_PATH =  "./experiments/concats/new_papers.csv"

# import os
# print("Current working directory:", os.getcwd())

CSS = """
        <style>
            /* General styling */
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }

            /* Content container */
            #content {
                max-width: 1200px;
                margin: 40px auto;
                padding: 0 20px;
            }

            /* Headings */
            h1 { 
                font-size: 28px;
                color: #1a1a1a;
                margin-bottom: 24px;
                border-bottom: 2px solid #1a1a1a;
                padding-bottom: 8px;
            }

            h2 { font-size: 24px; color: #2e3d49; margin: 20px 0; }
            h3 { font-size: 20px; color: #2e3d49; margin: 16px 0; }
            h4 { font-size: 18px; color: #2e3d49; margin: 14px 0; }
            h5 { font-size: 16px; color: #2e3d49; margin: 12px 0; }

            /* Tables */
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            th, td {
                border: 1px solid #e0e0e0;
                padding: 12px;
                text-align: left;
                word-wrap: break-word;  /* Enables soft wrapping of text */
                white-space: normal;    /* Allows wrapping of text inside the cells */
                max-width: 120px; 
            }

            th {
                background-color: #f5f5f5;
                font-weight: bold;
            }

            tr:nth-child(even) {
                background-color: #fafafa;
            }

            tr:hover {
                background-color: #f0f0f0;
            }

            /* Images */
            .image-container {
                margin: 20px 0;
                text-align: center;
            }

            .table-image {
                max-width: 90%;
                height: auto;
                display: inline-block;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* Dividers */
            hr {
                border: none;
                border-top: 1px solid #e0e0e0;
                margin: 30px 0;
            }
        </style>
        <div id="content">
        """