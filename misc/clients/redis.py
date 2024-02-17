import logging

from redis import Redis
from django.conf import settings

logger = logging.getLogger(__name__)


__all__ = ('statestore_redis', )


class SingletonRedisClient:
    instance = None

    @classmethod
    def get_instance(cls, conf: dict) -> Redis:
        """
        Get or generate a new instance of the class based on the gSiven configuration.

        :param conf: The configuration to be used for creating the instance.
        :type conf: Any

        :return: The newly created or existing instance.
        :rtype: Redis
        """
        logger.info("===== Redis Configuration =====")
        logger.info(conf)
        logger.info("===============================")
        
        # Check if an instance has already been created
        if cls.instance is None:
            # Create a new instance using the provided configuration
            cls.instance = Redis(**conf)
            logger.info(cls.instance.ping())


        # Return the newly created or existing instance
        return cls.instance


statestore_redis = SingletonRedisClient.get_instance({
    'host': settings.REDIS_HOST,
    'port': settings.REDIS_PORT,
    'db': settings.REDIS_DB,
    'password': settings.REDIS_PASSWORD
})