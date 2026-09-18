import requests

class PRT_API:

    def __init__(self, api_key):
        self.base_pred_link = "http://realtime.portauthority.org/bustime/api/v3/getpredictions?key=" + api_key

    def parse_pred(self, pred: dict):
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
            prediction_data.append({"id": id, "rt": rt, "prdtm": prdtm, "psgld": psgld})
        return prediction_data


    def get_pred(self, stop_id: int):
        """
            Sample link for predicition buses
            http://realtime.portauthority.org/bustime/api/v3/getpredictions?key=&tmres=s&localestring=en_US&format=json&rt=61C&stpid=4123
            Stop_id - Set value determined by Pittsburgh PRT
            7097 - Island
        """
        link = self.base_pred_link + "&tmres=s&rtpidatafeed=Port%20Authority%20Bus&localestring=en_US&format=json&stpid=" + str(stop_id)
        print(link)
        result = requests.get(link)
        result.raise_for_status()
        return self.parse_pred(result.json())
