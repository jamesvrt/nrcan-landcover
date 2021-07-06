import os.path
from tempfile import TemporaryDirectory

import pystac

from stactools.nrcan_landcover.commands import create_nrcanlandcover_command
from stactools.testing import CliTestCase

from tests import test_data


class CreateCollectionTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_nrcanlandcover_command]

    def test_create_catalog(self):
        with TemporaryDirectory() as tmp_dir:
            result = self.run_command(["nrcanlandcover", "create-catalog", tmp_dir])
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            catalog = pystac.read_file(os.path.join(tmp_dir, "catalog.json"))
            item_ids = set([item.id for item in catalog.get_all_items()])
            print(item_ids)
            # self.assertEqual(
            #     item_ids,
            #     set([])
            # )

    def test_create_cog(self):
        with TemporaryDirectory() as tmp_dir:
            test_path = test_data.get_path("data-files")
            paths = [
                os.path.join(test_path, d)
                for d in os.listdir(test_path)
                if d.lower().endswith(".tif")
            ]

            for path in paths:
                result = self.run_command(
                    ["nrcanlandcover", "create-cog", "-d", tmp_dir, "-s", path]
                )
                self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

                cogs = [p for p in os.listdir(tmp_dir) if p.endswith("_cog.tif")]
                self.assertEqual(len(cogs), 1)

    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:
            result = self.run_command(
                ["nrcanlandcover", "create-item", "-d", tmp_dir, "-c", "mock.tif"]
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()
