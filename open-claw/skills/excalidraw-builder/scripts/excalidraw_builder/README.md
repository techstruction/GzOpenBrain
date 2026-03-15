# Excalidraw Builder Skill Documentation 🎨

This documentation covers how to utilize the `Excalidraw Builder` within your 3-Layer Architecture. The skill converts textual reasoning or parsed data into visually appealing `.excalidraw` diagram files that you can load natively.

## What is the Excalidraw Builder?

The **Excalidraw Builder** is an agentic tool designed to scaffold interactive diagrams. Rather than trying to place lines on a canvas blindly, an agent (like Claude) interprets your request, figures out the logical blocks (nodes) and connections (edges), constructs an intermediate JSON structure dynamically, and asks the Python deterministic engine (`execution/excalidraw_builder/generate.sh`) to spit out a perfect native Excalidraw file.

---

## 🚀 How to use it (Basic Example)

You can ask your agent to use the skill with natural language.

**User Prompt:**
> "Please use the Excalidraw skill to map out a simple login flow: User goes to Login Page, they submit credentials, the API validates it, and then they either go to the Dashboard (Success) or get an Error message (Fail)."

**What the Agent Does:**
1. The agent breaks this down into Nodes (`User`, `Login Page`, `API`, `Dashboard`, `Error`).
2. The agent assigns specific shapes (e.g., Diamonds for decisions, Ellipses for End States).
3. The agent calculates basic X/Y coordinates so they flow logically.
4. The agent writes `.tmp/login_flow.json` and runs `execution/excalidraw_builder/generate.sh .tmp/login_flow.json .tmp/login_flow.excalidraw`.
5. The agent tells you the file is ready.

---

## 🛠️ Use Cases & Specific Prompts

### 1. **Project Folder Analysis (Architecture Maps)**
You can have the agent read a directory and visualize its structure.

**User Prompt:**
> "Review my `src/` directory and use the Excalidraw builder to create a tree diagram showing my modules and how they connect."

**Agent Action:**
The agent runs `list_dir` on `src/`, creates a node for each directory/file, connects them hierarchically, and generates the layout.

### 2. **Database Schema / ERD Mapping**
You can document your Prisma schema or raw SQL tables.

**User Prompt:**
> "Read my `schema.prisma` file. Use the Excalidraw skill to draw an Entity Relationship Diagram (ERD). Use Rectangles for tables and denote connections between them."

### 3. **Infrastructure / Microservices Cloud Topologies**
Map out how different servers or services talk to each other.

**User Prompt:**
> "Draw an Excalidraw diagram for my cloud infrastructure. I have an Nginx load balancer connecting to 3 Node.js servers, which all connect to a single Postgres Database. Use ellipses for databases."

### 4. **Algorithm / Data Processing Flowcharts**
Ideal for visualizing complex logic before you code it.

**User Prompt:**
> "I need to build an OAuth 2.0 flow for LinkedIn. Can you create an Excalidraw flowchart detailing the steps: User clicks login, Redirect to LinkedIn, User authorizes, Callback to our server, Exchange Code for Token, Save to DB."

---

## 💾 Saving, Retrieving, and Viewing Output

The agent will typically generate files into your local `.tmp/` folder or any directly specified folder (like `<YOUR_PROJECT>/docs/diagrams/`).

**To view or retrieve the output:**
1. Once the agent says "Done!", look for the output file (e.g., `flowchart.excalidraw`).
2. Open your web browser and navigate to:
   - [excalidraw.com](https://excalidraw.com) (Public Service)
   - [excalidraw.techstruction.co](https://excalidraw.techstruction.co) (Your Instance)
3. Drag and drop the `.excalidraw` file directly into the browser window, or use the "Open Folder" / "Load" button in Excalidraw.
4. Edit the file natively! 

**To save your modifications:**
1. In Excalidraw, click the **Export** or **Save** menu.
2. Select **Save to disk**.
3. Overwrite the original `.excalidraw` file in your repository. The agent can read it later if necessary. 
*(Note: Excalidraw files are just JSON under the hood, so they can be securely committed to Git).*

---

## 🔌 API/Service Extensibility

If you are building an app and want the app itself to diagram user data dynamically:

1. **Local Server Setup:** 
   You can have the agent wrap `excalidraw_generator.py` in a FastAPI or Express server.
2. **REST API Endpoint:** 
   Your frontend sends the `nodes` and `edges` JSON to `localhost:8000/generate`.
3. **Response:** 
   The server responds with the `.excalidraw` file bits, which you can render continuously.

To scaffold this, simply prompt the agent:
> "Wrap the Excalidraw builder in a FastAPI route so my frontend can ping it."
