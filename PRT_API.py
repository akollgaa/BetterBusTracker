import requests
from datetime import datetime

class PRT_API:

    def __init__(self, api_key):
        self.base_pred_link = "http://realtime.portauthority.org/bustime/api/v3/getpredictions?key=" + api_key

    def __parse_pred(self, pred: dict):
        """
            Parse the prediction data from the API response

            Returns:
                A dictionary with the following keys:
                    - rt: The route number
                    - prdtm: The prediction time in format YYYYMMDD HH:MM:SS
                    - psgld: The number of passengers on the bus
        """

        prediction_data = []

        buses = pred.get("bustime-response").get("prd")
        for bus in buses:
            id = bus.get("vid")
            rt = bus.get("rt")
            prdtm = bus.get("prdtm")
            psgld = bus.get("psgld")
            # prt : True - tracked bus : False - scheduled bus
            prediction_data.append({"id": id, 
                                    "rt": rt, 
                                    "prdtm": prdtm, 
                                    "psgld": psgld, 
                                    "prt": True})
        return prediction_data


    def get_prt_buses(self, stop_id: int):
        """
            Sample link for predicition buses
            http://realtime.portauthority.org/bustime/api/v3/getpredictions?key=&tmres=s&localestring=en_US&format=json&rt=61C&stpid=4123
            Stop_id - Set value determined by Pittsburgh PRT
            7097 - Island
        """
        link = self.base_pred_link + "&tmres=s&rtpidatafeed=Port%20Authority%20Bus&localestring=en_US&format=json&stpid=" + str(stop_id)
        result = requests.get(link)
        result.raise_for_status()
        return self.__parse_pred(result.json())

    def get_scheduled_bus(self):
        """
            Gets a list of scheduled buses for the 7097 bus stop
            returns:
                - A list of dictionaries that contain each scheduled bus within 30 minutes 
                based on the current time
        """

        results = []
        with open("newer_stop_times.csv", "r") as file:
            past_first = False
            weekday_value = datetime.now().weekday()
            weekday = "MF"
            if weekday_value == 5:
                weekday = "S"
            elif weekday_value == 6:
                weekday = "SH"
            for line in file:
                if not past_first: # Skip the header
                    past_first = True
                    continue
                entries = line.rstrip().split(",")
                if entries[3] != weekday:
                    continue
                arrival_time = datetime.time(datetime.strptime(entries[1], "%H:%M"))
                current_date = datetime.date(datetime.now())
                arrival_date = datetime.combine(current_date, arrival_time)
                diff = arrival_date - datetime.now()
                total_seconds = max(0, int(diff.total_seconds()))

                if((total_seconds <= 1800 and total_seconds > 0)): # 30 minutes
                    # Same format as tracked buses from __parsed_pred()
                    results.append({"id": entries[0], 
                                    "rt": entries[2], 
                                    "prdtm": arrival_date.strftime("%Y%m%d %H:%M:%S"), 
                                    "psgld": "HALF",
                                    "prt": False})
        return results

    def get_pred(self, stop_id: int):
        prt_buses = self.get_prt_buses(stop_id)
        scheduled_buses = self.get_scheduled_bus()

        combined_buses = []

        # This solution might be chopped but that's okay O(N^2) :(
        for scheduled in scheduled_buses:
            add_bus = True
            for prt in prt_buses:
                if prt.get("rt") == scheduled.get("rt"):
                    prt_time = datetime.strptime(prt.get("prdtm"), "%Y%m%d %H:%M:%S")
                    sch_time = datetime.strptime(scheduled.get("prdtm"), "%Y%m%d %H:%M:%S")
                    diff_time = abs(int((prt_time - sch_time).total_seconds()))
                    if diff_time <= 300: # +/-5 minute time difference
                        add_bus = False
                        break
            if add_bus:
                combined_buses.append(scheduled)

        combined_buses += prt_buses
        return combined_buses
