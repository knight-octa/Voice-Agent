import random
import copy
import json
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# === Terminal UTF-8 Support ===
sys.stdout.reconfigure(encoding='utf-8')

# === Flask App Setup ===
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# === Seller Data Store ===
sellers_data_store = [
    {'Seller Name': 'SneakerXpress', 'Price ($)': 280, 'Delivery Time (days)': 2, 'Availability': 'In Stock', 'Contact Number': '9525996352'},
    {'Seller Name': 'QuickKicks', 'Price ($)': 270, 'Delivery Time (days)': 4, 'Availability': 'In Stock', 'Contact Number': '9832939291'},
    {'Seller Name': 'StreetSole', 'Price ($)': 299, 'Delivery Time (days)': 1, 'Availability': 'In Stock', 'Contact Number': '8976892362'},
    {'Seller Name': 'ShoeResellHub', 'Price ($)': 275, 'Delivery Time (days)': 3, 'Availability': 'In Stock', 'Contact Number': '7692385467'},
    {'Seller Name': 'KickSmart', 'Price ($)': 285, 'Delivery Time (days)': 2, 'Availability': 'In Stock', 'Contact Number': '8924093178'},
]

# === Negotiation Simulation ===
def simulate_negotiation(seller_original):
    seller = copy.deepcopy(seller_original)
    original_price = seller['Price ($)']
    negotiated_price = original_price
    negotiation_attempted = original_price > 275
    negotiation_successful = False

    if negotiation_attempted and random.choice([True, False]):
        discount = random.randint(5, 15)
        negotiated_price = original_price - discount
        negotiation_successful = True

    return {
        'seller_name': seller['Seller Name'],
        'original_price': original_price,
        'negotiated_price': negotiated_price,
        'delivery_time_days': seller['Delivery Time (days)'],
        'availability': seller['Availability'],
        'contact_number': seller['Contact Number'],
        'negotiation_attempted': negotiation_attempted,
        'negotiation_successful': negotiation_successful,
        'order_confirmation': f"SIM-ORD{random.randint(1000,9999)}"
    }

def get_all_seller_offers_with_negotiation(product_name="sneakers"):
    return [simulate_negotiation(s) for s in sellers_data_store]

def get_top_deals_from_offers(all_offers, count=3):
    return sorted(all_offers, key=lambda x: (x['negotiated_price'], x['delivery_time_days']))[:count]

# === Console Simulation ===
def simulate_call(seller):
    print(f"\n📞 Calling {seller['Seller Name']} at {seller['Contact Number']}...")
    print(f"{seller['Seller Name']}: Price is ${seller['Price ($)']}, delivery in {seller['Delivery Time (days)']} days.")

    if random.choice([True, False]):
        discount = random.randint(5, 15)
        new_price = seller['Price ($)'] - discount
        print(f"Agent: Can you offer a better price?")
        print(f"{seller['Seller Name']}: Okay, new price is ${new_price}.")
        seller['Final Price'] = new_price
    else:
        print(f"{seller['Seller Name']}: Sorry, no discount available.")
        seller['Final Price'] = seller['Price ($)']

    seller['Final Delivery Time'] = seller['Delivery Time (days)']
    seller['Order Confirmation'] = f"ORD{random.randint(1000,9999)}"
    return seller

def get_top_deals_console():
    final_offers = [simulate_call(copy.deepcopy(seller)) for seller in sellers_data_store]
    top_deals = sorted(final_offers, key=lambda x: (x['Final Price'], x['Final Delivery Time']))[:3]

    print("\n✅ Top 3 Offers:")
    for offer in top_deals:
        print(f"\n🛒 Seller: {offer['Seller Name']}")
        print(f"💰 Final Price: ${offer['Final Price']}")
        print(f"🚚 Delivery: {offer['Final Delivery Time']} days")
        print(f"🧾 Confirmation: {offer['Order Confirmation']}")
    return top_deals

# === Flask Routes ===
@app.route('/')
def index():
    return "✅ Flask App is Running. Try /get-sneaker-deals"

@app.route('/get-sneaker-deals', methods=['GET'])
def api_get_sneaker_deals():
    product_name = request.args.get('product', 'sneakers')
    max_price = request.args.get('max_price', type=int)
    max_days = request.args.get('max_days', type=int)

    all_offers = get_all_seller_offers_with_negotiation(product_name)

    if max_price:
        all_offers = [offer for offer in all_offers if offer['negotiated_price'] <= max_price]
    if max_days:
        all_offers = [offer for offer in all_offers if offer['delivery_time_days'] <= max_days]

    top_3 = get_top_deals_from_offers(all_offers)

    return jsonify({
        "product_searched": product_name,
        "top_3_deals": top_3,
        "all_offers": all_offers
    })

# === Voice Agent Integration ===
try:
    from omnidimension import Client

    def create_negotiation_agent():
        api_key = os.getenv("OMNIDIMENSION_API_KEY", "zZoXIY6fCb4Xg_RRLs43xVmPQU7DL3z_g3XpwICYaMc")
        client = Client(api_key)

        response = client.agent.create(
            name="Price Negotiation Agent",
            welcome_message="Hello! This is Knight calling on behalf of Shivam...",
            context_breakdown=[
                {"title": "Agent Intro", "body": "Explain you're calling to negotiate sneaker prices."},
                {"title": "Negotiate", "body": "Ask for discount or faster delivery."},
            ],
            transcriber={"provider": "deepgram_stream", "model": "nova-3"},
            model={"model": "gpt-4o-mini", "temperature": 0.7},
            voice={"provider": "eleven_labs", "voice_id": "JBFqnCBsd6RMkjVDRZzb"},
            post_call_actions={
                "email": {
                    "enabled": True,
                    "recipients": ["shivamsinghgdc89@gmail.com"],
                    "include": ["summary", "extracted_variables"],
                    "subject": "Negotiation Summary",
                    "body": "Hi Shivam,\nHere's the deal summary..."
                },
                "webhook": {
                    "enabled": True,
                    "url": os.getenv("WEBHOOK_URL", "https://script.google.com/macros/s/..."),
                    "include": ["extracted_variables"]
                },
                "extracted_variables": [
                    {"key": "reseller_name", "prompt": "What is the reseller's name?"},
                    {"key": "final_price", "prompt": "What is the final agreed price?"}
                ]
            }
        )
        print("✅ Agent Created! ID:", response.get("id"))
        return response.get("id")

except ImportError:
    def create_negotiation_agent():
        print("⚠️ omnidimension not installed.")
        return "mock-agent-id"

# === Run App ===
if __name__ == "__main__":
    print("🔧 Console Simulation Running...")
    get_top_deals_console()

    print("\n🎙️ Voice Agent Bootstrapping...")
    create_negotiation_agent()

    print("\n🚀 Starting Flask App...")
    app.run(debug=True, port=5000)
