#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json
from fbpcs.private_computation.entity.cloud_provider import CloudProvider


@dataclass_json
@dataclass
class PCEConfig:
    subnets: List[str]
    cluster: str
    region: str
    onedocker_task_definition: str
    cloud_provider: CloudProvider = CloudProvider.AWS

    def __str__(self) -> str:
        # pyre-ignore
        return self.to_json()
