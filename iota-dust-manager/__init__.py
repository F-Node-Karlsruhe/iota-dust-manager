"""
iota-dust-manager

A python package that manages your receiving dust addresses.
"""

__version__ = "0.1.0"
__author__ = 'F-Node-Karlsruhe'


import iota_client

IOTA_DUST = 1_000_000

SWIPE_THRESHOLD = 2 * IOTA_DUST


class DustManager:

    def __init__(self,
                seed:str=None,
                node:str='https://api.hornet-1.testnet.chrysalis2.com',
                number_of_dust_transactions:int = 10,
                swipe_address:str=None
                ) -> None:
        
        if seed is None:
            raise Exception('Canot allow dust without giving a dust seed')
        
        self._seed = seed

        self._number_of_dust_transactions = number_of_dust_transactions

        self._client = iota_client.Client(nodes_name_password=[[node]])

        self._balance = self.client.get_balance(self.seed)

        self._dust_address = self.client.get_unspent_address(self.seed)[0] # TODO: get fixed address (first)

        self._swipe_address = swipe_address

        if self._balance < IOTA_DUST:

            print('Not enough funds to allow dust!')

            print('Please transfer at least %s IOTA to address %s', (IOTA_DUST, self.dust_address))

            return
        
        if self._balance < number_of_dust_transactions * 100_000:

            self._number_of_dust_transactions = int(self._balance / 100_000)
            
            print('Not enough funds to support %s dust transactions at once. Reducing to %s',
            (number_of_dust_transactions, self._number_of_dust_transactions))

        self._working_balance = 100_000 * self._number_of_dust_transactions

        if self._swipe_address is None:

            self._swipe_address = None #TODO: get fixed swipe addess (second)

        if not self.__is_dust_enabled():

            self.__refresh_dust()


    def __is_dust_enabled(self):

        address_balance_pair = self.client.get_address_balances([self._dust_address])[0]

        if address_balance_pair['dust_allowed']:

            return True

        return False

    def __refresh_dust(self) -> None:

        # update own balance
        self._balance = self.client.get_balance(self.seed)

        swipe_outputs = None

        if self._balance > SWIPE_THRESHOLD:

            swpie_outputs = [
            {
                'address': self._swipe_address,
                'amount': self._balance - self._working_balance,
            }
            ]

        # send the working balance to the dust address wit dust allowance
        message = self._client.message(
        seed=self._seed,
        outputs=swipe_outputs,
        dust_allowance_outputs=[
            {
                'address': self._dust_address,
                'amount': self._working_balance,
            }
            ]
        )

        self.client.retry_until_included(message_id = message['message_id'])
        
        # reset counter

    def get_dust_address(self) -> str:
        # TODO: count events to check dust still allowed
        return self._dust_address
