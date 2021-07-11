"""
iota-dust-manager

A thread safe python package that manages your receiving dust addresses.
"""

__version__ = "0.1.3"
__author__ = 'F-Node-Karlsruhe'


import iota_client
import threading

IOTA_DUST = 1_000_000

IOTA_PER_DUST_TRANSACTION = 100_000


class DustManager:
    """Create a DustManager.
    :param seed: The managers own seed. Create a seperate seed for this and don't use
                 your principal seed.
    :param node: The url of the node to use for the iota client used by the dust manager.
    :param number_of_dust_transactions: How many dust transactions are possible before
                                        the dust alloance must be refreshed on the dust address.
                                        Must be between 10 and 100.
                                        Default is ``10``.
                                        Reminder: for 10 dust transactions you need 1 Mi.
                                        Max is 100 dust transactions for 10 Mi.
    :param swipe_address: The address where the excess IOTAs on the dust address are transfered to.
                          If not specified a dedicated address is generated for this purpose and
                          the funds can be accessed by calling the ``pay_out(iota_address)``
                          function.
    :param swipe_threshold: Specifies the amount of IOTAs which shall be swiped to the
                            ``swipe_address`` if the ``dust_address`` exceeds this amount.
                            Default: 1_000_000
    """

    def __init__(self,
                seed:str=None,
                node:str=None,
                number_of_dust_transactions:int = 10,
                swipe_address:str=None,
                swipe_threshold:int=IOTA_DUST
                ) -> None:
        
        if seed is None:
            raise Exception('Canot allow dust without giving a dust seed')

        if node is None:

            node = 'https://api.hornet-1.testnet.chrysalis2.com'

            print('Warning: using the testnet with %s' % node)

        if swipe_threshold < IOTA_DUST:
            raise Exception('Swipe threshold mus be at least %s IOTA' % IOTA_DUST)

        if number_of_dust_transactions > 100 or number_of_dust_transactions < 10:
            raise Exception('number_of_dust_transactions must between 10 and 100!')
        
        self._seed = seed

        self._check_lock = threading.Lock()

        self._number_of_dust_transactions = number_of_dust_transactions

        self._client = iota_client.Client(nodes_name_password=[[node]])

        addresses = self._client.get_addresses(
                        seed=seed,
                        input_range_begin=0,
                        input_range_end=2,
                    )

        self._dust_address = addresses[0][0]

        self._swipe_address = swipe_address

        self._dust_balance = self._client.get_address_balances([self._dust_address])[0]['balance']

        if self._dust_balance < IOTA_DUST:

            print('Please transfer at least %s IOTA to address %s' % (IOTA_DUST, self._dust_address))

            raise Exception('Not enough funds to allow dust!')

        
        if self._dust_balance < number_of_dust_transactions * IOTA_PER_DUST_TRANSACTION:

            self._number_of_dust_transactions = int(self._dust_balance / IOTA_PER_DUST_TRANSACTION)
            
            print('Not enough funds to support %s dust transactions at once. Reducing to %s' %
            (number_of_dust_transactions, self._number_of_dust_transactions))

        self._working_balance = IOTA_PER_DUST_TRANSACTION * self._number_of_dust_transactions

        self._dust_counter = self._number_of_dust_transactions - len(self._client.find_outputs(addresses=[self._dust_address]))

        if self._swipe_address is None:

            self._swipe_address = addresses[1][0]

        self._swipe_threshold = swipe_threshold

        if not self.__check_dust_allowance():

            self.__refresh_dust()



    def __check_dust_active(self):

        with self._check_lock:

            self._dust_counter -= 1
            
            # rather be one too early than one too late
            if self._dust_counter > 1:

                return

            self.__refresh_dust()


    def __check_dust_allowance(self) -> bool:

        address_balance_pair = self._client.get_address_balances([self._dust_address])[0]

        if address_balance_pair['dust_allowed']:

            return True

        return False



    def __refresh_dust(self) -> None:

        # update own balance
        self._dust_balance = self._client.get_address_balances([self._dust_address])[0]['balance']

        swipe_outputs = None

        dust_allowance_output_amount = self._working_balance

        if self._dust_balance - self._working_balance > self._swipe_threshold:

            # swipe all dust to the swipe address
            swipe_outputs = [
            {
                'address': self._swipe_address,
                'amount': self._dust_balance - self._working_balance,
            }
            ]

        else:
            
            # merge all dust if not enough funds for swiping
            dust_allowance_output_amount = self._dust_balance

        # send the dust balance to the dust address wit dust allowance
        message = self._client.message(
        seed=self._seed,
        outputs=swipe_outputs,
        dust_allowance_outputs=[
            {
                'address': self._dust_address,
                'amount': dust_allowance_output_amount,
            }
            ]
        )

        self._client.retry_until_included(message_id = message['message_id'])
        
        # reset counter
        self._dust_counter = self._number_of_dust_transactions


 

    def get_dust_address(self, for_transaction:bool = True) -> str:
        """Returns a valid dust address with ``dust_allowance``
        :param for_transaction: If the returned address is used for a transaction and shall
                                be undergo the dust checks.
                                Default: ``True``
        """
        
        if for_transaction:

            threading.Thread(target=self.__check_dust_active).start()

        return self._dust_address

    def pay_out(self, iota_address:str = None) -> str:
        """Pays out the entire balance available above the ``working_balance`` to
        the specified iota address.
        Alternatively you can define a dedicated swipe address on creation to pay out
        the summoned dust transactions directly.
        :param iota_address: The iota address to which the funds shall be payed out.
        """

        pay_out_amount = self._client.get_balance(self._seed) - self._working_balance

        output = {
            'address': iota_address,
            'amount': pay_out_amount
        }
        self._client.message(seed=self._seed, outputs=[output])

