#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import defaultdict
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fbpcp.entity.mpc_instance import MPCParty
from fbpcs.common.entity.pcs_mpc_instance import PCSMPCInstance
from fbpcs.onedocker_binary_config import OneDockerBinaryConfig
from fbpcs.private_computation.entity.private_computation_instance import (
    PrivateComputationGameType,
    PrivateComputationInstance,
    PrivateComputationRole,
)
from fbpcs.private_computation.entity.private_computation_instance import (
    PrivateComputationInstanceStatus,
)
from fbpcs.private_computation.repository.private_computation_game import GameNames
from fbpcs.private_computation.service.compute_metrics_stage_service import (
    ComputeMetricsStageService,
)
from fbpcs.private_computation.service.constants import (
    NUM_NEW_SHARDS_PER_FILE,
)


class TestComputeMetricsStageService(IsolatedAsyncioTestCase):
    @patch("fbpcp.service.mpc.MPCService")
    def setUp(self, mock_mpc_svc):
        self.mock_mpc_svc = mock_mpc_svc
        self.mock_mpc_svc.create_instance = MagicMock()

        onedocker_binary_config_map = defaultdict(
            lambda: OneDockerBinaryConfig(
                tmp_directory="/test_tmp_directory/", binary_version="latest"
            )
        )
        self.stage_svc = ComputeMetricsStageService(
            onedocker_binary_config_map, self.mock_mpc_svc
        )

    async def test_compute_metrics(self):
        private_computation_instance = self._create_pc_instance()
        mpc_instance = PCSMPCInstance.create_instance(
            instance_id=private_computation_instance.instance_id + "_compute_metrics0",
            game_name=GameNames.LIFT.value,
            mpc_party=MPCParty.CLIENT,
            num_workers=private_computation_instance.num_mpc_containers,
        )

        self.mock_mpc_svc.start_instance_async = AsyncMock(return_value=mpc_instance)

        test_server_ips = [
            f"192.0.2.{i}"
            for i in range(private_computation_instance.num_mpc_containers)
        ]
        await self.stage_svc.run_async(private_computation_instance, test_server_ips)

        self.assertEqual(mpc_instance, private_computation_instance.instances[0])

    def test_get_game_args(self):
        # TODO: add game args test for attribution args
        private_computation_instance = self._create_pc_instance()
        test_game_args = [
            {
                "input_base_path": private_computation_instance.data_processing_output_path,
                "output_base_path": private_computation_instance.compute_stage_output_base_path,
                "file_start_index": 0,
                "num_files": private_computation_instance.num_files_per_mpc_container,
                "concurrency": private_computation_instance.concurrency,
            },
            {
                "input_base_path": private_computation_instance.data_processing_output_path,
                "output_base_path": private_computation_instance.compute_stage_output_base_path,
                "file_start_index": private_computation_instance.num_files_per_mpc_container,
                "num_files": private_computation_instance.num_files_per_mpc_container,
                "concurrency": private_computation_instance.concurrency,
            },
        ]

        self.assertEqual(
            test_game_args,
            self.stage_svc._get_compute_metrics_game_args(private_computation_instance),
        )

    def _create_pc_instance(self) -> PrivateComputationInstance:
        return PrivateComputationInstance(
            instance_id="test_instance_123",
            role=PrivateComputationRole.PARTNER,
            instances=[],
            status=PrivateComputationInstanceStatus.ID_MATCHING_COMPLETED,
            status_update_ts=1600000000,
            num_pid_containers=2,
            num_mpc_containers=2,
            num_files_per_mpc_container=NUM_NEW_SHARDS_PER_FILE,
            game_type=PrivateComputationGameType.LIFT,
            input_path="456",
            output_dir="789",
        )
