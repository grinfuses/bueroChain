import json
from datetime import datetime
from .block import Block

class Blockchain:
    def __init__(self, difficulty):
        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.mining_reward = 10
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], datetime.now().timestamp(), "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address):
        block = Block(
            len(self.chain),
            self.pending_transactions,
            datetime.now().timestamp(),
            self.get_latest_block().hash
        )
        
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = [
            {
                "from": "network",
                "to": miner_address,
                "amount": self.mining_reward
            }
        ]

    def add_transaction(self, sender, recipient, amount):
        self.pending_transactions.append({
            "from": sender,
            "to": recipient,
            "amount": amount
        })

    def get_balance(self, address):
        balance = 0

        for block in self.chain:
            for transaction in block.transactions:
                if transaction["from"] == address:
                    balance -= transaction["amount"]
                if transaction["to"] == address:
                    balance += transaction["amount"]

        for transaction in self.pending_transactions:
            if transaction["from"] == address:
                balance -= transaction["amount"]
            if transaction["to"] == address:
                balance += transaction["amount"]

        return balance

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            if not current_block.is_valid(self.difficulty):
                return False

        return True

    def to_dict(self):
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": self.pending_transactions,
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward
        } 