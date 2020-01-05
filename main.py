import re
import requests


def convert_camel_to_snake(text: str):
    """
    Convert camel case strings to snake case strings

    :param text: text to convert
    :type text: str
    :returns: converted string
    :rtype: str
    """
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()


# HTTP Types
GET = 'GET'


class BaseAPI:
    """
    Basic API class for SAS API
    """
    endpoint = 'https://api.flysas.com'

    def __init__(self):
        pass

    def get_data(self, url: str, params: dict = None):
        """
        Make a get request
        """
        request = requests.get(f'{self.endpoint}{url}', params=params)
        return request.json()


class BookingFlows:
    POINTS = 'points'
    CASH = 'revenue'


class FlightOffers(BaseAPI):
    def __init__(self, *args, **kwargs):
        self.pricing_type = ''
        self.inbound_flights = {}
        self.outbound_flights = {}
        self.product_info = {}
        self.tabs_info = {}
        self.currency = {}
        self.links = []
        self.region_name = ''
        self.offer_id = ''
        self.outbound_lowest_fare = {}
        self.inbound_lowest_fare = {}
        self.is_outbound_intercontinental = False
        self.is_inbound_intercontinental = False
        self.booking_flow = ''
        self.type = {}

        super(FlightOffers, self).__init__(*args, **kwargs)

    def load(
        self: object,
        from_iata: str = '',
        to_iata: str = '',
        start_departure_date: str = '20200102',
        return_departure_date: str = '20200101',
        adults: int = 0,
        children: int = 0,
        infants: int = 0,
        youth: int = 0,
        booking_flow: str = BookingFlows.CASH,
        position: str = 'se',
        channel: str = 'web',
        display_type: str = 'upsell',
    ):
        """
        Load data from API to object

        :param from_iata: from destination IATA
        :param to_iata: to destination IATA
        """
        data = self.get_data(
            '/offers/flights',
            params={
                'from': from_iata,
                'to': to_iata,
                'inDate': return_departure_date,
                'outDate': start_departure_date,
                'adt': adults,
                'chd': children,
                'inf': infants,
                'yth': youth,
                'bookingFlow': booking_flow,
                'pos': position,
                'channel': channel,
                'displayType': display_type,
            },
        )

        # Loop through the data and update class attributes
        # with those values
        for attr in data.keys():
            # Convert the attribute in camelCase (API response)
            # to snake case so we can use snake case in the class
            conv_attr = convert_camel_to_snake(attr)

            # Update class attributes
            setattr(self, conv_attr, data[attr])

        return self


if __name__ == '__main__':
    flight_offers = FlightOffers()
    available_flights = flight_offers.load(
        from_iata='ARN',
        to_iata='CPH',
        start_departure_date='20200202',
        return_departure_date='20200303',
        adults=0,
        children=0,
        infants=0,
        youth=1,
    )

    print('\n')
    print('Outbound flights---------------------------\n')
    for key, outbound_flight in available_flights.outbound_flights.items():
        origin = (
            f'{outbound_flight["origin"]["code"]}'
            f' {outbound_flight["origin"]["name"]}'
            f' ({outbound_flight["originCountry"]["name"]}'
            f' - {outbound_flight["originCity"]["name"]})'
        )
        destination = (
            f'{outbound_flight["destination"]["code"]}'
            f' {outbound_flight["destination"]["name"]}'
            f' ({outbound_flight["destinationCountry"]["name"]}'
            f' - {outbound_flight["destinationCity"]["name"]})'
        )
        flight_duration = outbound_flight['connectionDuration']
        start_time_in_local = outbound_flight['startTimeInLocal']
        end_time_in_local = outbound_flight['endTimeInLocal']
        stops = 0

        # Outbound flight meta
        print('---------- Flight')
        print('')
        print(f'From {origin} at {start_time_in_local}')
        print(f'To {destination} at {end_time_in_local}')
        print(f'A total of {stops} stops')

        for segment in outbound_flight['segments']:
            print('')
            print('-- Segments')
            print('')
            print(f'Departure from {segment["departureAirport"]["code"]} - Terminal {segment["departureTerminal"]} - {segment["arrivalDateTimeInLocal"]}')
            print(f'Arrival to {segment["arrivalAirport"]["code"]} - Terminal {segment["arrivalTerminal"]} - {segment["arrivalDateTimeInLocal"]}')
            print('')
            print(f'Aircraft {segment["airCraft"]["name"]}')

        print('\n\n\n')
