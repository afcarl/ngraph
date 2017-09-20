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

#include <iostream>
#include <memory>
#include <vector>

namespace ngraph
{
    class Node;

    namespace element
    {
        class Type;
    }

    namespace descriptor
    {
        class TensorView;
        class PrimaryTensorView;

        class Tensor
        {
            friend class PrimaryTensorView;

        private:
            Tensor(const Tensor&) = delete;
            Tensor& operator=(const Tensor&) = delete;

            Tensor(const element::Type& element_type,
                   PrimaryTensorView*   tensor_view,
                   const Node*          parent,
                   size_t               value_index);

            std::string get_next_view_name();

        public:
            bool               is_output() const { return m_is_output; }
            bool               is_input() const { return m_is_input; }
            bool               is_persistent() const { return m_is_persistent; }
            const std::string& get_name() const { return m_name; }
        protected:
            const element::Type& m_element_type;
            PrimaryTensorView*   m_primary_tensor_view;
            bool                 m_is_output;
            bool                 m_is_input;
            bool                 m_is_persistent;
            std::string          m_name;
            size_t               m_next_view_id;
        };

        std::ostream& operator<<(std::ostream&, const Tensor&);
    }
}