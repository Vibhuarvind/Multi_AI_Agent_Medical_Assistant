import pandas as pd
import json
import math

class PharmacyAgent:

    def __init__(self,
                 inventory_file="Data/inventory.csv",
                 zipcode_file="Data/zipcodes.csv",
                 pharmacy_file="Data/pharmacies.json"):

        self.inventory = pd.read_csv(inventory_file)
        self.zipcodes = pd.read_csv(zipcode_file)
        
        with open(pharmacy_file,"r") as f:
            self.pharmacies = json.load(f)

    def _distance(self, lat1, lon1, lat2, lon2):
        """ Dummy Manhattan distance for POC """
        return abs(lat1-lat2) + abs(lon1-lon2)

    def _estimate_eta_fee(self, distance):
        """ Convert distance → ETA + delivery fee (POC Rules) """
        if distance <= 0.03:   return 20, 15
        if distance <= 0.07:   return 40, 25
        return 60, 40

    def find_matches(self, medicine_skus, user_lat=19.12, user_lon=72.84):
        """
        1. Filter inventory where sku in medicine list and qty > 0
        2. Match with pharmacies.json
        3. Compute nearest & delivery feasibility
        4. Return JSON for best match
        """

        if not medicine_skus:
            return {"message": "No medicines requested"}

        # Step 1: Inventory filter
        stock = self.inventory[self.inventory["sku"].isin(medicine_skus)]
        stock = stock[stock["qty"] > 0]

        if stock.empty:
            return {"message":"Requested medicines not available anywhere"}

        results=[]

        # Step 2: Join with pharmacy geo data
        for ph in self.pharmacies:
            ph_id = ph["id"]
            subset = stock[stock["pharmacy_id"] == ph_id]

            if subset.empty:
                continue

            dist = self._distance(user_lat, user_lon, ph["lat"], ph["lon"])
            eta, fee = self._estimate_eta_fee(dist)

            results.append({
                "pharmacy_id": ph_id,
                "items": subset[["sku","qty"]].to_dict(orient="records"),
                "eta_min": eta,
                "delivery_fee": fee,
                "distance": round(dist,3)
            })

        if not results:
            return {"message":"No pharmacy stocks required meds nearby"}

        # Step 3: sort by nearest → most items → lowest fee
        results = sorted(results, key=lambda x:(x["distance"], -len(x["items"]), x["delivery_fee"]))

        best = results[0]

        # Final response JSON for pharmacy match agent
        return {
            "pharmacy_id": best["pharmacy_id"],
            "items": best["items"],
            "eta_min": best["eta_min"],
            "delivery_fee": best["delivery_fee"]
        }
