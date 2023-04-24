"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import uuid
import hashlib
from threading import Lock, currentThread

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
        self.queue = []
        self.consumers = {}
        self.producers = {}

        self.mutex = Lock()
        self.prod_mutex = Lock()
        self.cart_mutex = Lock()
        self.print_mutex = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.prod_mutex:
            producer_id = str(uuid.uuid4())
            self.producers[producer_id] = 0
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        if self.producers[producer_id] < self.queue_size_per_producer:
            self.queue.append((product, producer_id))
            self.producers[producer_id] += 1
            return True

        return False

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
        
        first_product = next((x for x in self.queue if x[0] == product), None)
        if isinstance(first_product, tuple):
            self.consumers[cart_id].append(first_product)
            with self.cart_mutex:
                self.queue.remove(first_product)
                self.producers[first_product[1]] -= 1
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
        
        first_product = next(
                (x for x in self.consumers[cart_id] if x[0] == product), None)
        if isinstance(first_product, tuple):
            self.queue.append(first_product)
            with self.cart_mutex:
                self.consumers[cart_id].remove(first_product)
                self.producers[first_product[1]] += 1

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        
        for product in self.consumers[cart_id]:
            with self.print_mutex:
                print(
                    f"{currentThread().getName()} bought {product[0]}")
        return self.consumers[cart_id]
