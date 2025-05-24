import logging
from checkerchain.base.validator import BaseValidatorNeuron
from checkerchain.utils.config import config as get_config

class Validator(BaseValidatorNeuron):
    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self):
        # Implement your validation logic here.
        # This is called every step for each batch of miners.
        logging.info("Default forward called. Override this method with your logic.")
        return

def main():
    config = get_config(Validator)
    validator = Validator(config=config)
    validator.run()

if __name__ == '__main__':
    main()

