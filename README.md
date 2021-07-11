# iota-dust-manager
A thread safe, stateless python package that manages your receiving dust address

## Install
```
pip install iota-dust-manager
```

## Usage
### Basic
```python
from iota_dust_manager import DustManager

SEED = 'YOUR_SECRET_SEED_FOR_DUST'

dm = DustManager(seed = SEED)

# whenever you need to receive dust, just call this function
dust_address = dm.get_dust_address()

# if you want to access the funds and transfer them

YOUR_IOTA_ADDRESS = 'YOUR_IOTA_ADDRESS...'

dm.pay_out('YOUR_IOTA_ADDRESS')
```

On first startup you will get this kind of message if the seed was not preloaded with funds:
```
Please transfer at least 1000000 IOTA to address atoi1qqwlmnfq2xfjz8u6ejkdsqz4f3ua3wle9cetd97ppdzr9mdyue5pwvd435j
```

### With dedicated swipe address
To swipe the dust funds to an dedicated address whenever the threshold is reached,  
just specify it on creation
```python
from iota_dust_manager import DustManager

SEED = 'YOUR_SECRET_SEED_FOR_DUST'

YOUR_SWIPE_ADDRESS = 'atoi1qzr2qca680txhplug4dkyhyvgu3w7g7jeuw2jale2ht60el3u9el2v375fe'

dm = DustManager(seed = SEED, swipe_address = YOUR_SWIPE_ADDRESS)

# whenever you need to receive dust, just call this function
dust_address = dm.get_dust_address()

```
Further you can specify the threshold above which the dust address gets swiped to the swipe address.  
`1_000_000` is the default and minimum swipe threshold allowed if the swipe address has no dust allowance.  
```python
dm = DustManager(seed = SEED, swipe_address = YOUR_SWIPE_ADDRESS, swipe_threshold = 1_000_000)
```

### Use on the mainnet
The default node is `https://api.hornet-1.testnet.chrysalis2.com` on the testnet.  
If you want to use the mainnet, initialise the dust manager with a mainnet node like so:  
```python
dm = DustManager(seed = SEED, node = 'https://chrysalis-nodes.iota.org')
```
