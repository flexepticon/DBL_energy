
# **Data Handling and Processing Workflow**

This repository is designed for consistent and efficient data processing. Please adhere to the following steps when working with measurement data or modifying the repository.

---

## **Adding New Data**
To add new measurement data and ensure it is correctly recognized:

1. **Open the Repository in VS Code**  
   - Clone the repository if you haven’t already. Use the **Source Control** panel in VS Code or run the cloning process via the Command Palette:
     - Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on Mac).
     - Search for `Git: Clone`.
     - Enter the repository URL and select a local folder.

2. **Copy Your Data Folder**  
   - Drag and drop the folder containing your measurement data into the appropriate directory within the repository using the VS Code file explorer.

3. **Run the Script**  
   - Open the script file (e.g., `File for graphs.py`) in VS Code.  
   - Run the script using the **Run and Debug** panel (`Ctrl+Shift+D` or `Cmd+Shift+D` on Mac).  
   - Ensure the script executes without errors and renames the files.

4. **Commit and Push Changes**
   - Make sure that your file is saved(`Ctrl+S` or `Cmd+S` on Mac)
   - Stage the changes in the **Source Control** panel.
   - Add a meaningful commit message (e.g., "Added new measurement data").
   - Push the changes directly to the main branch using the **Source Control** interface.  

**⚠️ DO NOT CREATE NEW BRANCHES.**  
All work must remain on the main branch to maintain consistency and avoid potential issues with pushing changes.

---

## **Processing Data**
To process and visualize data:

1. Open the **`File for graphs.ipynb`** notebook in VS Code.  
   - Fill in the required fields, such as **time start**, **time end** and **folder name**, within the notebook.  
   - Execute the cells to process the data and generate the desired plots.

2. If you need plots for a specific experiment, use the existing **`File for graphs.ipynb`**.  
   - **⚠️ DO NOT CREATE NEW NOTEBOOKS.**  
     - Using additional notebooks can disrupt the workflow and lead to confusion.
   - **⚠️ DO NOT FORGET ABOUT FORMATTING.**
     - No formatting can also lead to confusion.

---

## **Processing Class Updates**
- If you modify the **processing class** or encounter errors while using it, notify the team immediately.  
- This ensures that everyone is aware of the changes and can avoid redundant or conflicting edits.

---

By following these guidelines, we ensure a consistent, efficient, and error-free workflow for managing and processing data within the repository.
