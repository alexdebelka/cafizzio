import json
import streamlit as st
import os
import pandas as pd
from datetime import datetime

# CSS pentru a schimba culorile și stilurile
st.markdown("""
    <style>
    .stButton>button {
        background-color: #F6C324;
        color: black;
    }
    .stRadio>div>div>label {
        color: #F6C324;
    }
    .stSidebar>div {
        background-color: #F6C324;
    }
    .stDataFrame>div>div>div>table {
        background-color: #F6C324;
    }
    .css-1aumxhk, .css-1aumxhk a {
        color: #F6C324;
    }
    .css-1aumxhk .css-1aumxhk, .css-1aumxhk .css-1aumxhk a {
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# JSON files for data storage
CLIENTS_FILE = 'clients.json'
PRODUCTS_FILE = 'products.json'

# JSON handling functions
def read_json(file):
    if not os.path.exists(file):
        st.error(f"The file {file} does not exist.")
        return []
    with open(file, 'r') as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            st.error(f"Error reading {file}. It may be malformed.")
            return []

def write_json(file, data):
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error writing to {file}: {e}")

# Add new client function
def add_client(code, name, email, phone, credits):
    clients = read_json(CLIENTS_FILE)
    new_client = {
        'id': len(clients) + 1,
        'code': code.lower(),
        'name': name.lower(),
        'email': email,
        'phone': phone,
        'credits': credits,
        'history': []
    }
    clients.append(new_client)
    write_json(CLIENTS_FILE, clients)

# Update client info function
def update_client(id, code, name, email, phone):
    clients = read_json(CLIENTS_FILE)
    for client in clients:
        if client['id'] == id:
            client['code'] = code.lower()
            client['name'] = name.lower()
            client['email'] = email
            client['phone'] = phone
    write_json(CLIENTS_FILE, clients)

# Find client by code function
def find_client_by_code(code):
    clients = read_json(CLIENTS_FILE)
    return [client for client in clients if client['code'] == code.lower()]

# Find client by name function
def find_client_by_name(name):
    clients = read_json(CLIENTS_FILE)
    return [client for client in clients if client['name'] == name.lower()]

# Update credits function
def update_credits(client_code, amount):
    clients = read_json(CLIENTS_FILE)
    for client in clients:
        if client['code'] == client_code.lower():
            client['credits'] += amount
    write_json(CLIENTS_FILE, clients)

# Add new product function
def add_product(name, price):
    products = read_json(PRODUCTS_FILE)
    new_product = {
        'id': len(products) + 1,
        'name': name,
        'price': price
    }
    products.append(new_product)
    write_json(PRODUCTS_FILE, products)

# Update product function
def update_product(product_id, name, price):
    products = read_json(PRODUCTS_FILE)
    for product in products:
        if product['id'] == product_id:
            product['name'] = name
            product['price'] = price
    write_json(PRODUCTS_FILE, products)

# Get products function
def get_products():
    return read_json(PRODUCTS_FILE)

# Add purchase history function
def add_purchase_history(client, products_purchased):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for product_name, quantity in products_purchased.items():
        if quantity > 0:
            client['history'].append({
                'timestamp': timestamp,
                'product': product_name,
                'quantity': quantity,
                'total_cost': quantity * next(product['price'] for product in get_products() if product['name'] == product_name)
            })

# Streamlit interface

# Add logo on the first page
logo_path = "logo.png"  # Replace with your logo file path
if os.path.exists(logo_path):
    st.image(logo_path, width=100)

st.title("CAFIZZIO")

menu = ["Purchase Products", "Find Client", "View History", "Add Client", "Update Credits", "Manage Products", "Edit Client Info"]
choice = st.sidebar.radio("Menu", menu)

if choice == "Add Client":
    st.subheader("Add Client")
    with st.form(key='add_client_form'):
        code = st.text_input("Code")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        credits = st.number_input("Credits (RON)", min_value=0.0)
        submit_button = st.form_submit_button(label='Add')
        if submit_button:
            add_client(code, name, email, phone, credits)
            st.success("Client added successfully")

elif choice == "Find Client":
    st.subheader("Find Client")
    with st.form(key='find_client_form'):
        search_by = st.radio("Search by", ("Code", "Name"))
        if search_by == "Code":
            code = st.text_input("Enter Code")
        elif search_by == "Name":
            name = st.text_input("Enter Name")
        submit_button = st.form_submit_button(label='Search')
        if submit_button:
            if search_by == "Code":
                clients = find_client_by_code(code)
            else:
                clients = find_client_by_name(name)
            if clients:
                df = pd.DataFrame(clients).drop(columns=['history'])
                df.rename(columns={'credits': 'credits (RON)'}, inplace=True)
                st.write("Client Found:")
                st.dataframe(df)
            else:
                st.warning("Client not found")
    st.subheader("All Clients")
    clients = read_json(CLIENTS_FILE)
    df = pd.DataFrame(clients).drop(columns=['history'])
    df.rename(columns={'credits': 'credits (RON)'}, inplace=True)
    st.dataframe(df)

elif choice == "Manage Products":
    st.subheader("Manage Products")
    products = get_products()
    product_names = [product['name'] for product in products]
    selected_product_name = st.selectbox("Select Product to Edit", product_names)
    selected_product = next((product for product in products if product['name'] == selected_product_name), None)
    
    if selected_product:
        with st.form(key='update_product_form'):
            new_name = st.text_input("Product Name", value=selected_product['name'])
            new_price = st.number_input("Product Price", min_value=0.0, value=selected_product['price'])
            submit_button = st.form_submit_button(label='Update Product')
            if submit_button:
                update_product(selected_product['id'], new_name, new_price)
                st.success("Product updated successfully")

    st.subheader("Add New Product")
    with st.form(key='add_product_form'):
        product_name = st.text_input("New Product Name")
        product_price = st.number_input("New Product Price", min_value=0.0)
        submit_button = st.form_submit_button(label='Add Product')
        if submit_button:
            add_product(product_name, product_price)
            st.success("Product added successfully")
    
    st.subheader("Product List")
    products = get_products()
    df = pd.DataFrame(products)
    st.dataframe(df)

elif choice == "Update Credits":
    st.subheader("Update Credits")
    with st.form(key='update_credits_form'):
        client_code = st.text_input("Client Code")
        amount = st.number_input("Amount (RON)", min_value=-999999.0, max_value=999999.0)
        submit_button = st.form_submit_button(label='Update')
        if submit_button:
            update_credits(client_code, amount)
            st.success("Credits updated successfully")

elif choice == "Purchase Products":
    st.subheader("Purchase Products")
    with st.form(key='purchase_form'):
        search_by = st.radio("Search Client by", ("Code", "Name"))
        if search_by == "Code":
            client_code = st.text_input("Enter Client Code")
        elif search_by == "Name":
            client_name = st.text_input("Enter Client Name")
        check_client_button = st.form_submit_button(label='Check Client')
        if check_client_button:
            if search_by == "Code":
                clients = find_client_by_code(client_code)
            else:
                clients = find_client_by_name(client_name)
            if clients:
                client = clients[0]
                st.success(f"Client found: {client['name'].capitalize()}")
                st.session_state['client'] = client
            else:
                st.error("Client not found")

    client = st.session_state.get('client', None)
    
    if client:
        with st.form(key='products_form'):
            products = get_products()
            cols = st.columns(4)  # Adjust the number of columns to display products in 4 lines
            product_quantities = {}
            for i, product in enumerate(products):
                with cols[i % 4]:
                    st.write(f"{product['name']} - {product['price']} RON")
                    product_quantities[product['name']] = st.number_input(f"Quantity", min_value=0, step=1, key=f"quantity_{i}")
            purchase_button = st.form_submit_button(label='Purchase')
            if purchase_button:
                total_cost = sum(product['price'] * quantity for product in products for name, quantity in product_quantities.items() if product['name'] == name)
                if client['credits'] >= total_cost:
                    client['credits'] -= total_cost
                    add_purchase_history(client, product_quantities)
                    clients = read_json(CLIENTS_FILE)
                    for c in clients:
                        if c['id'] == client['id']:
                            c.update(client)
                    write_json(CLIENTS_FILE, clients)
                    st.success(f"Purchase successful! Total cost: {total_cost} RON. Remaining credits: {client['credits']} RON.")
                else:
                    st.error(f"Not enough credits. Total cost: {total_cost} RON. Available credits: {client['credits']} RON.")

elif choice == "View History":
    st.subheader("View Purchase History")
    with st.form(key='view_history_form'):
        search_by = st.radio("Search by", ("Code", "Name"))
        if search_by == "Code":
            client_code = st.text_input("Enter Client Code")
        elif search_by == "Name":
            client_name = st.text_input("Enter Client Name")
        submit_button = st.form_submit_button(label='View History')
        if submit_button:
            if search_by == "Code":
                clients = find_client_by_code(client_code)
            else:
                clients = find_client_by_name(client_name)
            if clients:
                client = clients[0]
                if 'history' in client and client['history']:
                    history_df = pd.DataFrame(client['history'])
                    st.write(f"Purchase History for {client['name'].capitalize()}:")
                    st.dataframe(history_df)
                else:
                    st.write(f"No purchase history for {client['name'].capitalize()}.")
            else:
                st.warning("Client not found")

elif choice == "Edit Client Info":
    st.subheader("Edit Client Info")
    with st.form(key='search_client_form'):
        search_by = st.radio("Search by", ("Code", "Name"))
        if search_by == "Code":
            client_code = st.text_input("Enter Client Code")
        elif search_by == "Name":
            client_name = st.text_input("Enter Client Name")
        search_button = st.form_submit_button(label='Search')
        if search_button:
            if search_by == "Code":
                clients = find_client_by_code(client_code)
            else:
                clients = find_client_by_name(client_name)
            if clients:
                client = clients[0]
                st.session_state['edit_client'] = client
                st.write("Current Client Info:")
                st.write(client)
            else:
                st.warning("Client not found")

    if 'edit_client' in st.session_state:
        client = st.session_state['edit_client']
        st.subheader("Update Client Info")
        with st.form(key='edit_client_form'):
            code = st.text_input("Code", value=client['code'])
            name = st.text_input("Name", value=client['name'])
            email = st.text_input("Email", value=client['email'])
            phone = st.text_input("Phone", value=client['phone'])
            submit_button = st.form_submit_button(label='Update')
            if submit_button:
                update_client(client['id'], code, name, email, phone)
                st.success("Client info updated successfully")
