import sys

from environs import Env
from loguru import logger

from src.config import RevancedConfig
from src.downloader import Downloader
from src.parser import Parser
from src.patches import Patches


def main() -> None:
    env = Env()
    config = RevancedConfig(env)

    patcher = Patches(config)
    downloader = Downloader(config)
    parser = Parser(patcher, config)

    logger.info(f"Will Patch only {patcher.config.apps}")
    for app in patcher.config.apps:
        try:
            logger.info("Trying to build %s" % app)
            app_all_patches, version, is_experimental = patcher.get_app_configs(app)
            version = downloader.download_apk_to_patch(version, app)
            patcher.include_and_exclude_patches(app, parser, app_all_patches)
            logger.info(f"Downloaded {app}, version {version}")
            parser.patch_app(app=app, version=version, is_experimental=is_experimental)
        except Exception as e:
            logger.exception(f"Failed to build {app} because of {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.error("Script halted because of keyboard interrupt.")
        sys.exit(-1)
