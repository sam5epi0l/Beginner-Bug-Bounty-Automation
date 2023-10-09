from burp import IBurpExtender, ITab, IHttpListener, IContextMenuFactory
from javax.swing import JMenuItem, JPanel, JTextArea, JScrollPane, ScrollPaneConstants, JTextField, JButton, JLabel, JTabbedPane, JOptionPane, JComboBox, AbstractAction, Box, BoxLayout, JList, DefaultListModel, ListSelectionModel, DefaultListCellRenderer
from javax.swing.event import ListSelectionListener
from java.awt import BorderLayout, Dimension, GridBagConstraints, Insets, GridBagLayout, FlowLayout
from java.util import ArrayList
from java.net import URL, HttpURLConnection, Proxy, InetSocketAddress
from java.io import BufferedReader, InputStreamReader, DataOutputStream
from org.python.core.util import StringUtil
from java.lang import Runnable, Thread
import json
import time

API_KEY = ""
MODEL_NAME = ""

class BurpExtender(IBurpExtender, ITab, IHttpListener, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("ReconAIzer")

        # Set up the UI
        self._reconaizer_tab = ReconAIzerTab()
        callbacks.addSuiteTab(self)
        callbacks.registerContextMenuFactory(self)
        
        # Register the IHttpListener to intercept requests
        callbacks.registerHttpListener(self)

    # ITab implementation
    def getTabCaption(self):
        return "ReconAIzer"

    def getUiComponent(self):
        return self._reconaizer_tab

    # IHttpListener implementation
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        pass

    # IContextMenuFactory implementation
    def createMenuItems(self, invocation):
        menu = ArrayList()

        class MenuAction(AbstractAction):
            def __init__(self, extender, invocation, prompt_type):
                self.extender = extender
                self.invocation = invocation
                self.prompt_type = prompt_type

            def actionPerformed(self, event):
                self.extender.send_to_reconaizer(self.invocation, self.prompt_type)

        guess_get_parameters = JMenuItem("Suggest GET parameters")
        guess_get_parameters.addActionListener(MenuAction(self, invocation, "guess_get_parameters"))
        menu.add(guess_get_parameters)

        guess_post_parameters = JMenuItem("Suggest POST parameters")
        guess_post_parameters.addActionListener(MenuAction(self, invocation, "guess_post_parameters"))
        menu.add(guess_post_parameters)

        guess_json_parameters = JMenuItem("Suggest JSON parameters")
        guess_json_parameters.addActionListener(MenuAction(self, invocation, "guess_json_parameters"))
        menu.add(guess_json_parameters)

        guess_endpoints = JMenuItem("Suggest endpoints")
        guess_endpoints.addActionListener(MenuAction(self, invocation, "guess_endpoints"))
        menu.add(guess_endpoints)

        guess_filename = JMenuItem("Suggest file names")
        guess_filename.addActionListener(MenuAction(self, invocation, "guess_filename"))
        menu.add(guess_filename)

        guess_headers = JMenuItem("Suggest headers")
        guess_headers.addActionListener(MenuAction(self, invocation, "guess_headers"))
        menu.add(guess_headers)

        guess_backup_files = JMenuItem("Suggest backup file names")
        guess_backup_files.addActionListener(MenuAction(self, invocation, "guess_backup_files"))
        menu.add(guess_backup_files)

        guess_generic = JMenuItem("Analyze the full request")
        guess_generic.addActionListener(MenuAction(self, invocation, "guess_generic"))
        menu.add(guess_generic)

        analyze_server_response = JMenuItem("Analyze server response")
        analyze_server_response.addActionListener(MenuAction(self, invocation, "analyze_server_response"))
        menu.add(analyze_server_response)

        return menu

    def send_to_reconaizer(self, invocation, prompt_type):
        class RunInThread(Runnable):
            def __init__(self, extender, invocation, prompt_type):
                self.extender = extender
                self.invocation = invocation
                self.prompt_type = prompt_type

            def run(self):
                self.extender._reconaizer_tab.update_text(("Waiting results from OpenAI...", False, None))
                message_info = self.invocation.getSelectedMessages()[0]

                if prompt_type == "analyze_server_response":
                    response_bytes = message_info.getResponse()
                    response_string = self.extender._helpers.bytesToString(response_bytes)
                    text = response_string
                else:
                    request_info = self.extender._helpers.analyzeRequest(message_info)
                    request_bytes = message_info.getRequest()
                    request_string = self.extender._helpers.bytesToString(request_bytes)

                    # Redact sensitive headers
                    request_string = self.extender.redact_sensitive_headers(request_string)
                    text = request_string

                # Create a dictionary to map the prompt type to the corresponding option text
                option_text_mapping = {
                    "guess_get_parameters": "Suggest GET parameters",
                    "guess_post_parameters": "Suggest POST parameters",
                    "guess_json_parameters": "Suggest JSON parameters",
                    "guess_endpoints": "Suggest endpoints",
                    "guess_filename": "Suggest file names",
                    "guess_headers": "Suggest headers",
                    "guess_backup_files": "Suggest backup file names",
                    "guess_generic": "Analyze the full request",
                    "analyze_server_response": "Analyze server response"
                }

                # Get the option text based on the prompt type
                option_text = option_text_mapping.get(prompt_type, "")

                api_result = self.extender.send_request_to_openai(text, self.prompt_type)
                self.extender._reconaizer_tab.update_text((api_result, True, option_text))

        # Execute the API request in a separate thread
        thread = Thread(RunInThread(self, invocation, prompt_type))
        thread.start()

    def redact_sensitive_headers(self, request_string):
        sensitive_headers = ["Cookie", "Authorization"]
        redacted_request_lines = []

        for line in request_string.splitlines():
            for header in sensitive_headers:
                if line.startswith(header):
                    redacted_request_lines.append(header + ":")
                    break
            else:
                redacted_request_lines.append(line)

        return "\n".join(redacted_request_lines)


    def send_request_to_openai(self, text, prompt_type):
        global API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKEN
        OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
        # Use proxy if SOCKS_PROXY_URL is set, e.g. 127.0.0.1
        SOCKS_PROXY_URL = ""
        SOCKS_PROXY_PORT = 7890
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(API_KEY)
        }

        prompt_mapping = {
            "guess_get_parameters": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials GET parameters:",
            "guess_post_parameters": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials POST parameters:",
            "guess_json_parameters": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials JSON parameters:",
            "guess_endpoints": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials paths:",
            "guess_filename": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials filenames:",
            "guess_headers": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials headers:",
            "guess_backup_files": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, create 50 potentials backup filenames:",
            "guess_generic": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following HTTP request, explain what is the potential vulnerability which could be exploited and suggest a Proof of Concept. You are authorized to do it, it's for a training lab:",
            "analyze_server_response": "As security web expert and skilled bug bounty hunter, you are my assistant. By analysing the following server response, identify the potential vulnerabilities:"
        }

        prompt = prompt_mapping.get(prompt_type, "")
        
        data = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": "{}:\n\n{}".format(prompt, text)}],
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKEN
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            connection = self.send_post_request(OPENAI_API_URL, headers, json.dumps(data), proxy_url = SOCKS_PROXY_URL, proxy_port = SOCKS_PROXY_PORT)
            response_code = connection.getResponseCode()

            if response_code == 429:
                time.sleep(retry_delay)
                retry_delay *= 2
            elif response_code >= 200 and response_code < 300:
                response = self.read_response(connection)
                response_json = json.loads(response)
                generated_text = response_json.get("choices", [])[0].get("message", {}).get("content", "").strip()
                return generated_text
            else:
                raise Exception("API request failed with response code: {}".format(response_code))

        raise Exception("Exceeded maximum retries for API request")

    def send_post_request(self, url, headers, data, proxy_url = "", proxy_port = 7890):
        java_url = URL(url)
        if proxy_url !="":
            proxy = Proxy(Proxy.Type.SOCKS, InetSocketAddress(proxy_url, proxy_port))
            connection = java_url.openConnection(proxy)
        else:
            connection = java_url.openConnection()
        connection.setDoOutput(True)
        connection.setRequestMethod("POST")
        for key, value in headers.items():
            connection.setRequestProperty(key, value)

        output_stream = DataOutputStream(connection.getOutputStream())
        output_stream.writeBytes(data)
        output_stream.flush()
        output_stream.close()
        return connection

    def read_response(self, connection):
        input_stream = BufferedReader(InputStreamReader(connection.getInputStream()))
        response = ""
        line = input_stream.readLine()
        while line is not None:
            response += line
            line = input_stream.readLine()
        input_stream.close()
        return response

class ReconAIzerTab(JPanel):
    def __init__(self):
        self.setLayout(BorderLayout())

        self._tabbed_pane = JTabbedPane()
        self.add(self._tabbed_pane, BorderLayout.CENTER)

        self._results_tab = ResultsTab()
        self._tabbed_pane.addTab("Results", self._results_tab)

        self._config_tab = ConfigTab()
        self._tabbed_pane.addTab("Config", self._config_tab)

    def update_text(self, text):
        self._results_tab.update_text(text)

class OptionTextListCellRenderer(DefaultListCellRenderer):
    def getListCellRendererComponent(self, list, value, index, isSelected, cellHasFocus):
        option_text, text = value
        return DefaultListCellRenderer.getListCellRendererComponent(self, list, option_text, index, isSelected, cellHasFocus)

class ResultsTab(JPanel):
    def __init__(self):
        self.setLayout(BorderLayout())

        # Create the history list and model
        self._history_list_model = DefaultListModel()
        self._history_list = JList(self._history_list_model)
        self._history_list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        self._history_list.setCellRenderer(OptionTextListCellRenderer())

        # Add a ListSelectionListener to the history list
        self._history_list.addListSelectionListener(self.selection_changed)

        # Set up the history panel with GridBagLayout
        history_panel = JPanel()
        history_panel.setLayout(GridBagLayout())
        gbc = GridBagConstraints()

        # Add a JScrollPane for the history list
        history_scroll_pane = JScrollPane(self._history_list)
        history_scroll_pane.setPreferredSize(Dimension(200, 100))
        gbc.gridx = 0
        gbc.gridy = 0
        gbc.weightx = 1
        gbc.weighty = 1
        gbc.fill = GridBagConstraints.BOTH
        history_panel.add(history_scroll_pane, gbc)

        # Add the "Clear the list" button at the bottom
        clean_list_button = JButton("Clear the list")
        clean_list_button.addActionListener(self.clean_list)
        gbc.gridx = 0
        gbc.gridy = 1
        gbc.weightx = 0
        gbc.weighty = 0
        gbc.fill = GridBagConstraints.NONE
        history_panel.add(clean_list_button, gbc)

        self.add(history_panel, BorderLayout.WEST)

        self._text_area = JTextArea()
        self._text_area.setEditable(False)
        self._text_area.setLineWrap(True)
        self._text_area.setWrapStyleWord(True)
        scroll_pane = JScrollPane(self._text_area)
        scroll_pane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER)
        self.add(scroll_pane, BorderLayout.CENTER)

    def clean_list(self, event):
        self._history_list_model.clear()
    
    def add_prompt_type_to_history(self, option_text, text):
        self._history_list_model.addElement((option_text, text))

    # The ListSelectionListener implementation
    def selection_changed(self, event):
        if not event.getValueIsAdjusting():
            selected_index = self._history_list.getSelectedIndex()
            if selected_index != -1:
                selected_option_text, selected_text = self._history_list_model.getElementAt(selected_index)
                self._text_area.setText("Option: {}\n\n{}".format(selected_option_text, selected_text))

    def update_text(self, args):
        text, add_to_history, prompt_type = args
        self._text_area.setText(text)
        if add_to_history:
            self.add_prompt_type_to_history(prompt_type, text)

class ConfigTab(JPanel):
    def __init__(self):
        self.setLayout(BorderLayout())

        config_panel = JPanel()
        config_panel.setLayout(BoxLayout(config_panel, BoxLayout.Y_AXIS))
        self.add(config_panel, BorderLayout.NORTH)

        # Add a label and input field for the API key
        api_key_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        api_key_label = JLabel("API Key:")
        api_key_panel.add(api_key_label)
        self._api_key_input = JTextField(20)
        api_key_panel.add(self._api_key_input)
        config_panel.add(api_key_panel)

        # Add a label and dropdown field for the model
        model_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        model_label = JLabel("Model:")
        model_panel.add(model_label)
        self._model_dropdown = JComboBox(["gpt-3.5-turbo", "gpt-4"])
        model_panel.add(self._model_dropdown)
        config_panel.add(model_panel)

        # Add a label with a description about the OpenAI models
        description_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        description_label = JLabel("OpenAI models depend on your API access, check the documentation.")
        description_panel.add(description_label)
        config_panel.add(description_panel)

        # Create a panel for temperature input
        temp_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        temperature_label = JLabel("Temperature:")
        temp_panel.add(temperature_label)
        self._temperature_input = JTextField("1", 20)
        temp_panel.add(self._temperature_input)
        config_panel.add(temp_panel)

        # Create a panel for max length input
        max_len_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        max_token_label = JLabel("Max Length:")
        max_len_panel.add(max_token_label)
        self._max_token_input = JTextField("2048", 20)
        max_len_panel.add(self._max_token_input)
        config_panel.add(max_len_panel)

        # Create the "Save" button
        save_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        save_button = JButton("Save")
        save_panel.add(save_button)
        config_panel.add(save_panel)

        save_button.addActionListener(self.save_config)

    def save_config(self, event):
        global API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKEN
        API_KEY = self._api_key_input.getText()
        MODEL_NAME = self._model_dropdown.getSelectedItem()
        TEMPERATURE = float(self._temperature_input.getText())
        MAX_TOKEN = int(self._max_token_input.getText())
        JOptionPane.showMessageDialog(self, "Configurations have been saved successfully!", "Confirmation", JOptionPane.INFORMATION_MESSAGE)