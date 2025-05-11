from src.integrations.infrastructure.external_api.headhunter.adapter import HeadHunterAdapter


def get_headhunter_adapter() -> HeadHunterAdapter:
    """
    Dependency provider for the HeadHunter API client.

    Creates and returns a client configured to interact with the HeadHunter external API.

    :return: An instance of HeadHunterClient.
    """
    return HeadHunterAdapter()
