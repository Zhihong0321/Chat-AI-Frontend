"""
Gradio UI for GraphRAG Chatbot.
"""
import os
import gradio as gr
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
# For standalone frontend deployment, use API_BASE_URL environment variable
# Example: API_BASE_URL=https://graphrag-api.railway.app
API_BASE = os.getenv('API_BASE_URL', 'http://localhost:8000')
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me")

print(f"🔗 Frontend connecting to API: {API_BASE}")
print(f"🔑 Admin token configured: {'Yes' if ADMIN_TOKEN != 'change-me' else 'No (using default)'}")


def create_ui():
    """Create Gradio interface."""
    
    with gr.Blocks(title="GraphRAG Chatbot", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🤖 GraphRAG Knowledge Chatbot")
        gr.Markdown("Upload documents, create chat profiles, and query your knowledge base.")
        
        with gr.Tabs():
            # Tab 1: Knowledge Vault (Folder-based document management)
            with gr.Tab("🗄️ Knowledge Vault"):
                gr.Markdown("### Folder Management")
                gr.Markdown("Organize your documents into isolated knowledge vaults")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        folder_name_input = gr.Textbox(
                            label="New Folder Name",
                            placeholder="e.g., Legal Documents, Technical Specs",
                            max_lines=1
                        )
                        create_folder_btn = gr.Button("Create Folder", variant="primary")
                        folder_create_status = gr.Textbox(label="Status", interactive=False, lines=2)
                    
                    with gr.Column(scale=2):
                        refresh_folders_btn = gr.Button("🔄 Refresh Folder List")
                        folder_list = gr.Dataframe(
                            headers=["Folder Name", "Documents", "Status", "Last Indexed"],
                            label="Knowledge Vaults",
                            interactive=False,
                            wrap=True
                        )
                
                gr.Markdown("---")
                gr.Markdown("### Document Upload")
                
                with gr.Row():
                    with gr.Column():
                        folder_selector = gr.Dropdown(
                            label="Select Target Folder",
                            choices=[],
                            info="Choose which folder to upload documents to"
                        )
                        file_upload_multi = gr.File(
                            label="Upload Documents",
                            file_count="multiple",
                            file_types=[".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".png", ".jpg"],
                            type="filepath"
                        )
                        upload_to_folder_btn = gr.Button("Upload to Folder", variant="primary")
                        upload_folder_status = gr.Textbox(label="Upload Status", interactive=False, lines=3)
                    
                    with gr.Column():
                        refresh_docs_btn = gr.Button("🔄 Refresh Document List")
                        document_list = gr.Dataframe(
                            headers=["Filename", "Size", "Status", "Uploaded"],
                            label="Documents in Selected Folder",
                            interactive=False,
                            wrap=True
                        )
                
                gr.Markdown("---")
                gr.Markdown("### Indexing")
                gr.Markdown("⚠️ **Important:** Documents must be indexed before they can be queried by agents.")
                
                with gr.Row():
                    with gr.Column():
                        index_folder_btn = gr.Button("🔄 Index Selected Folder", variant="primary")
                        check_status_btn = gr.Button("📊 Check Folder Status", variant="secondary")
                        test_api_btn = gr.Button("🔍 Test API Connection", variant="secondary")
                    with gr.Column():
                        indexing_status = gr.Textbox(
                            label="Indexing Status",
                            interactive=False,
                            lines=6,
                            placeholder="Select a folder and click 'Index Selected Folder' to start indexing"
                        )
                
                # Event handlers for Knowledge Vault tab
                def create_folder(name):
                    if not name or not name.strip():
                        return "❌ Please enter a folder name"
                    
                    try:
                        response = httpx.post(
                            f"{API_BASE}/folders/create",
                            json={"name": name.strip()},
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            return f"✅ Folder '{result['name']}' created successfully!\nFolder ID: {result['folder_id']}"
                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                            return f"❌ Failed: {error_data.get('detail', 'Unknown error')}"
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                
                def list_folders():
                    try:
                        response = httpx.get(f"{API_BASE}/folders/list", timeout=10.0)
                        if response.status_code == 200:
                            folders = response.json()
                            if not folders:
                                return [["No folders created yet", "0", "not_indexed", ""]]
                            
                            return [[
                                f['name'],
                                str(f['document_count']),
                                f['status'],
                                f['last_indexed'][:19] if f['last_indexed'] else "Never"
                            ] for f in folders]
                        else:
                            return [["Error loading folders", "", "", ""]]
                    except Exception as e:
                        return [[f"Error: {str(e)}", "", "", ""]]
                
                def get_folder_choices():
                    try:
                        response = httpx.get(f"{API_BASE}/folders/list", timeout=10.0)
                        if response.status_code == 200:
                            folders = response.json()
                            return gr.Dropdown(choices=[(f['name'], f['folder_id']) for f in folders])
                        else:
                            return gr.Dropdown(choices=[])
                    except Exception as e:
                        return gr.Dropdown(choices=[])
                
                def upload_to_folder(folder_id, files):
                    if not folder_id:
                        return "❌ Please select a folder first"
                    
                    if not files:
                        return "❌ Please select files to upload"
                    
                    results = []
                    success_count = 0
                    fail_count = 0
                    
                    file_list = files if isinstance(files, list) else [files]
                    
                    for file_path in file_list:
                        try:
                            with open(file_path, 'rb') as f:
                                files_data = {'file': (os.path.basename(file_path), f)}
                                response = httpx.post(
                                    f"{API_BASE}/folders/{folder_id}/upload",
                                    files=files_data,
                                    timeout=60.0
                                )
                            
                            if response.status_code == 200:
                                result = response.json()
                                results.append(f"✅ {os.path.basename(file_path)}: Success")
                                success_count += 1
                            else:
                                results.append(f"❌ {os.path.basename(file_path)}: {response.text[:50]}")
                                fail_count += 1
                        except Exception as e:
                            results.append(f"❌ {os.path.basename(file_path)}: {str(e)[:50]}")
                            fail_count += 1
                    
                    summary = f"Upload complete: {success_count} succeeded, {fail_count} failed\n\n"
                    if success_count > 0:
                        summary += "⚠️ NEXT STEP: Scroll down and click 'Index Selected Folder' to make documents queryable!\n\n"
                    return summary + "\n".join(results)
                
                def list_folder_documents(folder_id):
                    if not folder_id:
                        return [["Select a folder to view documents", "", "", ""]]
                    
                    try:
                        response = httpx.get(f"{API_BASE}/folders/{folder_id}/documents", timeout=10.0)
                        if response.status_code == 200:
                            docs = response.json()
                            if not docs:
                                return [["No documents in this folder", "", "", ""]]
                            
                            return [[
                                d['title'],
                                f"{d.get('size', 0) / 1024:.1f} KB" if d.get('size') else "N/A",
                                d['status'],
                                d['uploaded_at'][:19] if d.get('uploaded_at') else "N/A"
                            ] for d in docs]
                        else:
                            return [["Error loading documents", "", "", ""]]
                    except Exception as e:
                        return [[f"Error: {str(e)}", "", "", ""]]
                
                def index_folder(folder_id):
                    if not folder_id:
                        return "❌ Please select a folder first"
                    
                    try:
                        url = f"{API_BASE}/folders/{folder_id}/index"
                        print(f"[DEBUG] Calling indexing endpoint: {url}")
                        
                        response = httpx.post(
                            url,
                            json={"method": "fast"},
                            timeout=30.0  # Increased timeout
                        )
                        
                        print(f"[DEBUG] Response status: {response.status_code}")
                        print(f"[DEBUG] Response body: {response.text[:500]}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            return f"✅ Indexing started!\nJob ID: {result.get('job_id', 'N/A')}\nStatus: {result.get('status', 'Processing')}\nMessage: {result.get('message', 'N/A')}\n\nThis may take several minutes. Click 'Check Folder Status' to monitor progress."
                        elif response.status_code == 202:
                            # Accepted - job queued
                            result = response.json()
                            return f"✅ Indexing job queued!\nJob ID: {result.get('job_id', 'N/A')}\nStatus: {result.get('status', 'Queued')}\n\nClick 'Check Folder Status' to monitor progress."
                        else:
                            try:
                                error_data = response.json()
                                error_msg = error_data.get('detail', error_data.get('message', error_data.get('error', 'Unknown error')))
                            except:
                                error_msg = response.text[:500]
                            return f"❌ Indexing Failed (HTTP {response.status_code})\n\nError: {error_msg}\n\nURL: {url}"
                    except httpx.TimeoutException:
                        return f"❌ Request timed out after 30 seconds\n\nThe API took too long to respond.\nURL: {API_BASE}/folders/{folder_id}/index"
                    except httpx.ConnectError:
                        return f"❌ Connection failed\n\nCannot connect to API.\nURL: {API_BASE}/folders/{folder_id}/index"
                    except Exception as e:
                        return f"❌ Unexpected Error\n\n{type(e).__name__}: {str(e)}\n\nURL: {API_BASE}/folders/{folder_id}/index"
                
                def check_folder_status(folder_id):
                    """Check the current status of a folder's indexing."""
                    if not folder_id:
                        return "❌ Please select a folder first"
                    
                    try:
                        response = httpx.get(f"{API_BASE}/folders/{folder_id}/status", timeout=10.0)
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"[DEBUG] Status response: {result}")
                            
                            status = result.get('status', 'unknown')
                            folder_name = result.get('name', 'Unknown')
                            doc_count = result.get('document_count', 0)
                            error_msg = result.get('error_message', result.get('error', ''))
                            last_indexed = result.get('last_indexed', 'Never')
                            
                            status_emoji = {
                                'ready': '✅',
                                'indexing': '⏳',
                                'failed': '❌',
                                'not_indexed': '⚠️',
                                'parsed': '📄'
                            }.get(status, '❓')
                            
                            status_text = f"{status_emoji} Folder: {folder_name}\nStatus: {status}\nDocuments: {doc_count}\nLast Indexed: {last_indexed}"
                            
                            # Show all error information
                            if status == 'failed':
                                if error_msg:
                                    status_text += f"\n\n⚠️ Error Details:\n{error_msg}"
                                else:
                                    status_text += f"\n\n⚠️ Indexing failed but no error message was stored.\nCheck backend logs for details."
                                
                                # Show raw response for debugging
                                status_text += f"\n\n[DEBUG] Raw response:\n{str(result)[:300]}"
                            
                            return status_text
                        else:
                            return f"❌ Failed to check status (HTTP {response.status_code})\nResponse: {response.text[:200]}"
                    except Exception as e:
                        return f"❌ Error: {type(e).__name__}\n{str(e)}"
                
                def test_api_connection():
                    """Test connection to the backend API."""
                    try:
                        # Test folders list endpoint (should always work)
                        response = httpx.get(f"{API_BASE}/folders/list", timeout=5.0)
                        if response.status_code == 200:
                            folders = response.json()
                            return f"✅ API Connected!\n\nEndpoint: {API_BASE}\nStatus: OK\nFolders found: {len(folders)}"
                        else:
                            return f"⚠️ API responded but with status {response.status_code}\n\nEndpoint: {API_BASE}\n\nTry checking backend logs."
                    except httpx.ConnectError:
                        return f"❌ Cannot connect to API\n\nEndpoint: {API_BASE}\n\nThe backend may be down or the URL is incorrect."
                    except httpx.TimeoutException:
                        return f"❌ Connection timeout\n\nEndpoint: {API_BASE}\n\nThe backend is not responding."
                    except Exception as e:
                        return f"❌ Error: {type(e).__name__}\n\n{str(e)}\n\nEndpoint: {API_BASE}"
                
                # Wire up event handlers
                create_folder_btn.click(
                    create_folder,
                    inputs=[folder_name_input],
                    outputs=[folder_create_status]
                ).then(
                    list_folders,
                    outputs=[folder_list]
                ).then(
                    get_folder_choices,
                    outputs=[folder_selector]
                )
                
                refresh_folders_btn.click(
                    list_folders,
                    outputs=[folder_list]
                ).then(
                    get_folder_choices,
                    outputs=[folder_selector]
                )
                
                upload_to_folder_btn.click(
                    upload_to_folder,
                    inputs=[folder_selector, file_upload_multi],
                    outputs=[upload_folder_status]
                ).then(
                    list_folder_documents,
                    inputs=[folder_selector],
                    outputs=[document_list]
                ).then(
                    list_folders,
                    outputs=[folder_list]
                )
                
                folder_selector.change(
                    list_folder_documents,
                    inputs=[folder_selector],
                    outputs=[document_list]
                )
                
                refresh_docs_btn.click(
                    list_folder_documents,
                    inputs=[folder_selector],
                    outputs=[document_list]
                )
                
                index_folder_btn.click(
                    index_folder,
                    inputs=[folder_selector],
                    outputs=[indexing_status]
                ).then(
                    list_folders,
                    outputs=[folder_list]
                )
                
                check_status_btn.click(
                    check_folder_status,
                    inputs=[folder_selector],
                    outputs=[indexing_status]
                ).then(
                    list_folders,
                    outputs=[folder_list]
                )
                
                test_api_btn.click(
                    test_api_connection,
                    outputs=[indexing_status]
                )
            
            # Tab 2: Document Ingestion (Legacy - kept for backward compatibility)
            with gr.Tab("📄 Ingest Documents"):
                gr.Markdown("### Upload Documents")
                gr.Markdown("Supported formats: PDF, DOCX, TXT, MD, CSV, XLSX, PNG, JPG (max 40MB)")
                
                with gr.Row():
                    with gr.Column():
                        file_upload = gr.File(
                            label="Upload Document",
                            file_types=[".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".png", ".jpg"],
                            type="filepath"
                        )
                        upload_btn = gr.Button("Upload", variant="primary")
                        upload_status = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Column():
                        refresh_docs_btn = gr.Button("🔄 Refresh Document List")
                        docs_list = gr.Dataframe(
                            headers=["Document ID", "Title", "Status", "Uploaded At"],
                            label="Uploaded Documents",
                            interactive=False
                        )
                
                def upload_document(file_path):
                    if not file_path:
                        return "Please select a file"
                    
                    try:
                        with open(file_path, 'rb') as f:
                            files = {'file': (os.path.basename(file_path), f)}
                            response = httpx.post(f"{API_BASE}/ingest/upload", files=files, timeout=60.0)
                        
                        if response.status_code == 200:
                            result = response.json()
                            return f"✅ Uploaded successfully! Doc ID: {result['doc_id']}\nStatus: {result['status']}"
                        else:
                            return f"❌ Upload failed: {response.text}"
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                
                def list_documents():
                    try:
                        response = httpx.get(f"{API_BASE}/ingest/list", timeout=10.0)
                        if response.status_code == 200:
                            docs = response.json()
                            if not docs:
                                return [["No documents uploaded yet", "", "", ""]]
                            return [[d['doc_id'][:8], d['title'], d['status'], d['uploaded_at'][:19]] for d in docs]
                        else:
                            return [["Error loading documents", "", "", ""]]
                    except Exception as e:
                        return [[f"Error: {str(e)}", "", "", ""]]
                
                upload_btn.click(upload_document, inputs=[file_upload], outputs=[upload_status])
                refresh_docs_btn.click(list_documents, outputs=[docs_list])
                
                # Indexing section
                gr.Markdown("### 🔄 Index Documents")
                gr.Markdown("Run GraphRAG indexing to build the knowledge graph from uploaded documents.")
                
                with gr.Row():
                    index_method = gr.Radio(
                        choices=["fast", "standard"],
                        value="fast",
                        label="Indexing Method",
                        info="Fast: quicker but less detailed. Standard: slower but more comprehensive."
                    )
                    index_btn = gr.Button("Start Indexing", variant="primary")
                    index_status = gr.Textbox(label="Indexing Status", interactive=False)
                
                def trigger_indexing(method):
                    try:
                        response = httpx.post(
                            f"{API_BASE}/admin/reindex",
                            json={"method": method},
                            headers={"X-Admin-Token": ADMIN_TOKEN},
                            timeout=10.0
                        )
                        if response.status_code == 200:
                            result = response.json()
                            return f"✅ Indexing started! Job ID: {result['job_id']}\nThis may take several minutes..."
                        else:
                            return f"❌ Failed: {response.text}"
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                
                index_btn.click(trigger_indexing, inputs=[index_method], outputs=[index_status])
            
            # Tab 2: Agents (Agent Management)
            with gr.Tab("🤖 Agents"):
                gr.Markdown("### Create and Manage Agents")
                gr.Markdown("Configure agents with access to specific knowledge folders")
                
                with gr.Row():
                    with gr.Column():
                        # Agent creation form
                        agent_name_input = gr.Textbox(
                            label="Agent Name",
                            placeholder="e.g., Legal Assistant, Tech Support Bot",
                            max_lines=1
                        )
                        agent_role_input = gr.Textbox(
                            label="Role Instructions",
                            placeholder="You are a helpful assistant that...",
                            lines=5,
                            info="Define the agent's behavior and personality"
                        )
                        
                        # Folder access selection
                        agent_folder_access = gr.CheckboxGroup(
                            label="Folder Access",
                            choices=[],
                            info="Select which folders this agent can access"
                        )
                        
                        gr.Markdown("### LLM Configuration")
                        
                        with gr.Row():
                            agent_llm_model = gr.Dropdown(
                                choices=[
                                    "gpt-5-nano-2025-08-07",
                                    "gpt-5-mini-2025-08-07",
                                    "deepseek-v3-2-exp",
                                    "qwen3-max",
                                    "gemini-2.5-flash"
                                ],
                                value="gpt-5-mini-2025-08-07",
                                label="LLM Model"
                            )
                            agent_temperature = gr.Slider(
                                minimum=0,
                                maximum=2,
                                value=0.7,
                                step=0.1,
                                label="Temperature",
                                info="Higher = more creative, Lower = more focused"
                            )
                        
                        with gr.Row():
                            agent_retrieval_method = gr.Radio(
                                choices=["global", "local"],
                                value="global",
                                label="Retrieval Method",
                                info="Global: broad context, Local: specific details"
                            )
                            agent_top_k = gr.Slider(
                                minimum=1,
                                maximum=50,
                                value=10,
                                step=1,
                                label="Top K Results",
                                info="Number of context items to retrieve"
                            )
                        
                        with gr.Row():
                            create_agent_btn = gr.Button("Create Agent", variant="primary")
                            update_agent_btn = gr.Button("Update Agent", variant="secondary")
                            clear_form_btn = gr.Button("Clear Form")
                        
                        agent_status = gr.Textbox(label="Status", interactive=False, lines=3)
                        
                        # Hidden field to store selected agent ID for editing
                        selected_agent_id = gr.State(value=None)
                    
                    with gr.Column():
                        refresh_agents_btn = gr.Button("🔄 Refresh Agent List")
                        agent_list = gr.Dataframe(
                            headers=["Name", "Folders", "Method", "Model", "Created", "Agent ID"],
                            label="Configured Agents",
                            interactive=False,
                            wrap=True
                        )
                        
                        gr.Markdown("### Agent Actions")
                        with gr.Row():
                            agent_id_input = gr.Textbox(
                                label="Agent ID",
                                placeholder="Enter agent ID to edit or delete",
                                max_lines=1
                            )
                            load_agent_btn = gr.Button("Load Agent", variant="secondary")
                            delete_agent_btn = gr.Button("Delete Agent", variant="stop")
                
                # Event handlers for Agents tab
                def get_folder_choices_for_agents():
                    """Get list of folders for checkbox group."""
                    try:
                        response = httpx.get(f"{API_BASE}/folders/list", timeout=10.0)
                        if response.status_code == 200:
                            folders = response.json()
                            # Return list of tuples (display_name, folder_id)
                            return gr.CheckboxGroup(
                                choices=[(f"{f['name']} ({f['document_count']} docs)", f['folder_id']) for f in folders]
                            )
                        else:
                            return gr.CheckboxGroup(choices=[])
                    except Exception as e:
                        return gr.CheckboxGroup(choices=[])
                
                def create_agent(name, role_instructions, folder_access, llm_model, temperature, retrieval_method, top_k):
                    """Create a new agent."""
                    if not name or not name.strip():
                        return "❌ Please enter an agent name (minimum 3 characters)", None
                    
                    if len(name.strip()) < 3:
                        return "❌ Agent name must be at least 3 characters", None
                    
                    if not role_instructions or not role_instructions.strip():
                        return "❌ Please enter role instructions", None
                    
                    if not folder_access or len(folder_access) == 0:
                        return "❌ Please select at least one folder", None
                    
                    try:
                        response = httpx.post(
                            f"{API_BASE}/agents/create",
                            json={
                                "name": name.strip(),
                                "role_instructions": role_instructions.strip(),
                                "folder_access": folder_access,
                                "retrieval_method": retrieval_method,
                                "top_k": int(top_k),
                                "llm_model": llm_model,
                                "temperature": float(temperature)
                            },
                            timeout=10.0
                        )
                        
                        if response.status_code == 201:
                            result = response.json()
                            return f"✅ Agent '{result['name']}' created successfully!\nAgent ID: {result['agent_id']}", None
                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                            return f"❌ Failed: {error_data.get('detail', 'Unknown error')}", None
                    except Exception as e:
                        return f"❌ Error: {str(e)}", None
                
                def list_agents():
                    """List all agents."""
                    try:
                        response = httpx.get(f"{API_BASE}/agents/list", timeout=10.0)
                        if response.status_code == 200:
                            agents = response.json()
                            if not agents:
                                return [["No agents created yet", "", "", "", "", ""]]
                            
                            # Get folder names for display
                            folders_response = httpx.get(f"{API_BASE}/folders/list", timeout=10.0)
                            folder_map = {}
                            if folders_response.status_code == 200:
                                folders = folders_response.json()
                                folder_map = {f['folder_id']: f['name'] for f in folders}
                            
                            return [[
                                a['name'],
                                ", ".join([folder_map.get(fid, fid[:8]) for fid in a['folder_access']]),
                                a['retrieval_method'],
                                a['llm_model'],
                                a['created_at'][:19] if a.get('created_at') else "N/A",
                                a['agent_id']
                            ] for a in agents]
                        else:
                            return [["Error loading agents", "", "", "", "", ""]]
                    except Exception as e:
                        return [[f"Error: {str(e)}", "", "", "", "", ""]]
                
                def load_agent(agent_id):
                    """Load agent configuration for editing."""
                    if not agent_id or not agent_id.strip():
                        return "❌ Please enter an agent ID", "", "", [], "gpt-4o-mini", 0.7, "global", 10, None
                    
                    try:
                        response = httpx.get(f"{API_BASE}/agents/{agent_id.strip()}", timeout=10.0)
                        
                        if response.status_code == 200:
                            agent = response.json()
                            status_msg = f"✅ Loaded agent '{agent['name']}' for editing"
                            
                            return (
                                status_msg,
                                agent['name'],
                                agent['role_instructions'],
                                agent['folder_access'],
                                agent['llm_model'],
                                agent['temperature'],
                                agent['retrieval_method'],
                                agent['top_k'],
                                agent['agent_id']
                            )
                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                            return f"❌ Failed: {error_data.get('detail', 'Unknown error')}", "", "", [], "gpt-4o-mini", 0.7, "global", 10, None
                    except Exception as e:
                        return f"❌ Error: {str(e)}", "", "", [], "gpt-4o-mini", 0.7, "global", 10, None
                
                def update_agent(agent_id, name, role_instructions, folder_access, llm_model, temperature, retrieval_method, top_k):
                    """Update an existing agent."""
                    if not agent_id:
                        return "❌ No agent loaded for editing. Please load an agent first.", agent_id
                    
                    if not name or not name.strip():
                        return "❌ Please enter an agent name (minimum 3 characters)", agent_id
                    
                    if len(name.strip()) < 3:
                        return "❌ Agent name must be at least 3 characters", agent_id
                    
                    if not role_instructions or not role_instructions.strip():
                        return "❌ Please enter role instructions", agent_id
                    
                    if not folder_access or len(folder_access) == 0:
                        return "❌ Please select at least one folder", agent_id
                    
                    try:
                        response = httpx.put(
                            f"{API_BASE}/agents/{agent_id}",
                            json={
                                "name": name.strip(),
                                "role_instructions": role_instructions.strip(),
                                "folder_access": folder_access,
                                "retrieval_method": retrieval_method,
                                "top_k": int(top_k),
                                "llm_model": llm_model,
                                "temperature": float(temperature)
                            },
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            return f"✅ Agent '{result['name']}' updated successfully!", None
                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                            return f"❌ Failed: {error_data.get('detail', 'Unknown error')}", agent_id
                    except Exception as e:
                        return f"❌ Error: {str(e)}", agent_id
                
                def delete_agent(agent_id):
                    """Delete an agent."""
                    if not agent_id or not agent_id.strip():
                        return "❌ Please enter an agent ID to delete"
                    
                    try:
                        response = httpx.delete(f"{API_BASE}/agents/{agent_id.strip()}", timeout=10.0)
                        
                        if response.status_code == 200:
                            result = response.json()
                            return f"✅ {result.get('message', 'Agent deleted successfully')}"
                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                            return f"❌ Failed: {error_data.get('detail', 'Unknown error')}"
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                
                def clear_form():
                    """Clear the agent form."""
                    return "", "", [], "gpt-4o-mini", 0.7, "global", 10, "Form cleared", None
                
                # Wire up event handlers
                create_agent_btn.click(
                    create_agent,
                    inputs=[
                        agent_name_input,
                        agent_role_input,
                        agent_folder_access,
                        agent_llm_model,
                        agent_temperature,
                        agent_retrieval_method,
                        agent_top_k
                    ],
                    outputs=[agent_status, selected_agent_id]
                ).then(
                    list_agents,
                    outputs=[agent_list]
                )
                
                update_agent_btn.click(
                    update_agent,
                    inputs=[
                        selected_agent_id,
                        agent_name_input,
                        agent_role_input,
                        agent_folder_access,
                        agent_llm_model,
                        agent_temperature,
                        agent_retrieval_method,
                        agent_top_k
                    ],
                    outputs=[agent_status, selected_agent_id]
                ).then(
                    list_agents,
                    outputs=[agent_list]
                )
                
                load_agent_btn.click(
                    load_agent,
                    inputs=[agent_id_input],
                    outputs=[
                        agent_status,
                        agent_name_input,
                        agent_role_input,
                        agent_folder_access,
                        agent_llm_model,
                        agent_temperature,
                        agent_retrieval_method,
                        agent_top_k,
                        selected_agent_id
                    ]
                )
                
                delete_agent_btn.click(
                    delete_agent,
                    inputs=[agent_id_input],
                    outputs=[agent_status]
                ).then(
                    list_agents,
                    outputs=[agent_list]
                ).then(
                    clear_form,
                    outputs=[
                        agent_name_input,
                        agent_role_input,
                        agent_folder_access,
                        agent_llm_model,
                        agent_temperature,
                        agent_retrieval_method,
                        agent_top_k,
                        agent_status,
                        selected_agent_id
                    ]
                )
                
                clear_form_btn.click(
                    clear_form,
                    outputs=[
                        agent_name_input,
                        agent_role_input,
                        agent_folder_access,
                        agent_llm_model,
                        agent_temperature,
                        agent_retrieval_method,
                        agent_top_k,
                        agent_status,
                        selected_agent_id
                    ]
                )
                
                refresh_agents_btn.click(
                    list_agents,
                    outputs=[agent_list]
                ).then(
                    get_folder_choices_for_agents,
                    outputs=[agent_folder_access]
                )
            
            # Tab 3: Chat Playground
            with gr.Tab("💬 Chat Playground"):
                gr.Markdown("### Interactive Chat with Agents")
                gr.Markdown("Select an agent and start a conversation based on your knowledge vaults")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        # Agent selector
                        chat_agent_selector = gr.Dropdown(
                            label="Select Agent",
                            choices=[],
                            info="Choose an agent to chat with"
                        )
                        refresh_chat_agents_btn = gr.Button("🔄 Refresh Agents")
                        
                        # Agent info display
                        agent_info_display = gr.Markdown("**No agent selected**")
                    
                    with gr.Column(scale=3):
                        # Chatbot component
                        chat_playground_chatbot = gr.Chatbot(
                            label="Conversation",
                            height=500,
                            show_label=True
                        )
                        
                        # Message input
                        chat_msg_input = gr.Textbox(
                            label="Your Message",
                            placeholder="Ask a question about your knowledge...",
                            lines=2,
                            max_lines=5
                        )
                        
                        with gr.Row():
                            chat_send_btn = gr.Button("Send", variant="primary")
                            chat_clear_btn = gr.Button("Clear History")
                        
                        # Citations accordion
                        with gr.Accordion("📚 Citations", open=False) as citations_accordion:
                            citations_dataframe = gr.Dataframe(
                                headers=["Folder", "Document", "Snippet"],
                                label="Source References",
                                interactive=False,
                                wrap=True
                            )
                
                # Hidden state for session management
                chat_session_id = gr.State(value=None)
                
                # Event handlers for Chat Playground
                def get_agent_choices_for_chat():
                    """Get list of agents for dropdown."""
                    try:
                        response = httpx.get(f"{API_BASE}/agents/list", timeout=10.0)
                        if response.status_code == 200:
                            agents = response.json()
                            if not agents:
                                return gr.Dropdown(choices=[])
                            # Return list of tuples (display_name, agent_id)
                            return gr.Dropdown(
                                choices=[(a['name'], a['agent_id']) for a in agents]
                            )
                        else:
                            return gr.Dropdown(choices=[])
                    except Exception as e:
                        return gr.Dropdown(choices=[])
                
                def display_agent_info(agent_id):
                    """Display selected agent information."""
                    if not agent_id:
                        return "**No agent selected**"
                    
                    try:
                        response = httpx.get(f"{API_BASE}/agents/{agent_id}", timeout=10.0)
                        if response.status_code == 200:
                            agent = response.json()
                            
                            # Get folder names
                            folders_response = httpx.get(f"{API_BASE}/folders/list", timeout=10.0)
                            folder_map = {}
                            if folders_response.status_code == 200:
                                folders = folders_response.json()
                                folder_map = {f['folder_id']: f['name'] for f in folders}
                            
                            folder_names = [folder_map.get(fid, fid[:8]) for fid in agent['folder_access']]
                            
                            info = f"""
**Agent:** {agent['name']}

**Accessible Folders:** {', '.join(folder_names)}

**Model:** {agent['llm_model']} | **Method:** {agent['retrieval_method']} | **Top K:** {agent['top_k']}
"""
                            return info
                        else:
                            return "**Error loading agent information**"
                    except Exception as e:
                        return f"**Error:** {str(e)}"
                
                def send_chat_message(agent_id, message, chat_history, session_id):
                    """Send message to agent and get response."""
                    if not agent_id:
                        return chat_history, [["Please select an agent first", "", ""]], session_id, ""
                    
                    if not message or not message.strip():
                        return chat_history, [["Please enter a message", "", ""]], session_id, ""
                    
                    # Add user message to chat history
                    chat_history.append((message, None))
                    
                    try:
                        # Prepare request payload
                        payload = {
                            "message": message.strip(),
                            "stream": False
                        }
                        
                        if session_id:
                            payload["session_id"] = session_id
                        
                        # Call chat API
                        response = httpx.post(
                            f"{API_BASE}/chat/{agent_id}/message",
                            json=payload,
                            timeout=120.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            answer = result['response']
                            citations = result.get('citations', [])
                            new_session_id = result.get('session_id', session_id)
                            
                            # Update chat history with response
                            chat_history[-1] = (message, answer)
                            
                            # Format citations for dataframe
                            if citations:
                                citations_data = []
                                for citation in citations:
                                    folder_name = citation.get('folder_name', 'Unknown')
                                    doc_title = citation.get('title', 'Unknown')
                                    snippet = citation.get('snippet', '')[:200] + "..." if len(citation.get('snippet', '')) > 200 else citation.get('snippet', '')
                                    citations_data.append([folder_name, doc_title, snippet])
                            else:
                                citations_data = [["No citations", "", ""]]
                            
                            return chat_history, citations_data, new_session_id, ""
                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                            error_msg = f"❌ Error: {error_data.get('detail', 'Unknown error')}"
                            chat_history[-1] = (message, error_msg)
                            return chat_history, [["Error occurred", "", ""]], session_id, ""
                    
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        chat_history[-1] = (message, error_msg)
                        return chat_history, [["Error occurred", "", str(e)]], session_id, ""
                
                def clear_chat_history(agent_id, session_id):
                    """Clear conversation history."""
                    if not agent_id:
                        return [], [["No agent selected", "", ""]], None
                    
                    try:
                        # Call clear history API if session exists
                        if session_id:
                            params = {"session_id": session_id}
                            response = httpx.delete(
                                f"{API_BASE}/chat/{agent_id}/clear",
                                params=params,
                                timeout=10.0
                            )
                        
                        return [], [["History cleared", "", ""]], None
                    except Exception as e:
                        return [], [[f"Error clearing history: {str(e)}", "", ""]], None
                
                def load_chat_history(agent_id, session_id):
                    """Load existing chat history when agent is selected."""
                    if not agent_id:
                        return [], [["No agent selected", "", ""]]
                    
                    try:
                        # Try to load recent history
                        params = {}
                        if session_id:
                            params["session_id"] = session_id
                        
                        response = httpx.get(
                            f"{API_BASE}/chat/{agent_id}/history",
                            params=params,
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            messages = result.get('messages', [])
                            
                            # Convert to chat history format
                            chat_history = []
                            for i in range(0, len(messages), 2):
                                if i + 1 < len(messages):
                                    user_msg = messages[i]['content']
                                    assistant_msg = messages[i + 1]['content']
                                    chat_history.append((user_msg, assistant_msg))
                            
                            return chat_history, [["History loaded", "", ""]]
                        else:
                            return [], [["No previous history", "", ""]]
                    except Exception as e:
                        return [], [[f"Error loading history: {str(e)}", "", ""]]
                
                # Wire up event handlers
                refresh_chat_agents_btn.click(
                    get_agent_choices_for_chat,
                    outputs=[chat_agent_selector]
                )
                
                chat_agent_selector.change(
                    display_agent_info,
                    inputs=[chat_agent_selector],
                    outputs=[agent_info_display]
                ).then(
                    load_chat_history,
                    inputs=[chat_agent_selector, chat_session_id],
                    outputs=[chat_playground_chatbot, citations_dataframe]
                )
                
                chat_send_btn.click(
                    send_chat_message,
                    inputs=[chat_agent_selector, chat_msg_input, chat_playground_chatbot, chat_session_id],
                    outputs=[chat_playground_chatbot, citations_dataframe, chat_session_id, chat_msg_input]
                )
                
                chat_msg_input.submit(
                    send_chat_message,
                    inputs=[chat_agent_selector, chat_msg_input, chat_playground_chatbot, chat_session_id],
                    outputs=[chat_playground_chatbot, citations_dataframe, chat_session_id, chat_msg_input]
                )
                
                chat_clear_btn.click(
                    clear_chat_history,
                    inputs=[chat_agent_selector, chat_session_id],
                    outputs=[chat_playground_chatbot, citations_dataframe, chat_session_id]
                )
        
        gr.Markdown("---")
        gr.Markdown("💡 **Tip:** Upload documents → Index them → Create agents → Start chatting!")
        
        # Load initial data when the app starts
        app.load(
            fn=lambda: (get_folder_choices(), get_folder_choices_for_agents()),
            outputs=[folder_selector, agent_folder_access]
        )
    
    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", os.getenv("PORT", "7860"))),
        share=False
    )
