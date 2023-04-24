"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import uuid
import hashlib
from productinformation import ProdInfo

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.queue_size_per_producer = queue_size_per_producer
        self.consumers = {}
        self.producers = {}

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        id = str(uuid.uuid4())
        self.producers[id] = []
        return id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        if self.producers[producer_id].len() >= self.queue_size_per_producer:
            return False
        
        self.producers[producer_id].append(product)
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        random_cart_id = str(uuid.uuid4())
        hashed_cart_id = hashlib.sha256(random_cart_id.encode())
        cut_down_hex = hashed_cart_id.hexdigest()[:8]
        cart_id = int(cut_down_hex, 16)
        cart_id = cart_id % 10000
        self.consumers[cart_id] = []
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        for producer_id in self.producers:
            if product in self.producers[producer_id]:
                self.producers[producer_id].remove(product)
                self.consumers[cart_id].append(ProdInfo(product, producer_id))
                return True
            
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        for prod in self.consumers[cart_id]:
            if prod.product == product:
                self.producers[prod.producer_id].append(product)
                self.consumers[cart_id].remove(prod)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return self.consumers[cart_id]
