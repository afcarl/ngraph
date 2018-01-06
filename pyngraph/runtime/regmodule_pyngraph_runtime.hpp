// ----------------------------------------------------------------------------
// Copyright 2017 Nervana Systems Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// ----------------------------------------------------------------------------

#pragma once

#include <pybind11/pybind11.h>
#include "pyngraph/runtime/backend.hpp"
#include "pyngraph/runtime/call_frame.hpp"
#include "pyngraph/runtime/external_function.hpp"
#include "pyngraph/runtime/manager.hpp"
#include "pyngraph/runtime/parameterized_tensor_view.hpp"
#include "pyngraph/runtime/tensor_view.hpp"
#include "pyngraph/runtime/utils.hpp"
#include "pyngraph/runtime/value.hpp"

namespace py = pybind11;

void regmodule_pyngraph_runtime(py::module m);
