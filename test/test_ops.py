#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Copyright 2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
import pytest
import numpy as np

import pyngraph.util as util
from pyngraph import Type, Function
from pyngraph.runtime import Manager
from pyngraph.op import Acos, Asin, Atan, Cos, Sin, Tan
from pyngraph.op import Cosh, Sinh, Tanh, Sqrt, Sign
from pyngraph.op import Power, Negative, Ceiling, Floor
from pyngraph.op import Parameter, Maximum, Minimum
from pyngraph.op import Add, Subtract, Multiply, Divide, Dot
from pyngraph.op import Constant, Abs, Exp, Log, Sum
from pyngraph.op import Greater, Less, Equal, NotEqual, GreaterEq, LessEq, Not
from pyngraph.op import OneHot, Broadcast, Reshape, Convert, Reduce
from pyngraph.op import Concat, Select
from pyngraph.op import Reverse, MaxPool, Convolution, ReplaceSlice, Slice


def make_backend_call_frame(function):

    manager = Manager.get(pytest.config.getoption('backend'));
    external = manager.compile(function)
    backend = manager.allocate_backend()
    cf = backend.make_call_frame(external)

    return backend, cf


def binary_op(op_str, a, b):

    if op_str == "+":
        return a + b
    elif op_str == "Add":
        return Add(a, b)
    elif op_str == "-":
        return a - b
    elif op_str == "Sub":
        return Subtract(a, b)
    elif op_str == "*":
        return a * b
    elif op_str == "Mul":
        return Multiply(a, b)
    elif op_str == "/":
        return a / b
    elif op_str == "Div":
        return Divide(a, b)
    elif op_str == "Dot":
        return Dot(a, b)
    elif op_str == "Equal":
        return Equal(a, b)
    elif op_str == "Greater":
        return Greater(a, b)
    elif op_str == "GreaterEq":
        return GreaterEq(a, b)
    elif op_str == "Less":
        return Less(a, b)
    elif op_str == "LessEq":
        return LessEq(a, b)
    elif op_str == "Maximum":
        return Maximum(a, b)
    elif op_str == "Minimum":
        return Minimum(a, b)
    elif op_str == "NotEqual":
        return NotEqual(a, b)
    elif op_str == "Power":
        return Power(a, b)


def binary_op_ref(op_str, a, b):

    if op_str == "+" or op_str == "Add":
        return a + b
    elif op_str == "-" or op_str == "Sub":
        return a - b
    elif op_str == "*" or op_str == "Mul":
        return a * b
    elif op_str == "/" or op_str == "Div":
        return a / b
    elif op_str == "Dot":
        return np.dot(a, b)
    elif op_str == "Equal":
        return np.equal(a, b)
    elif op_str == "Greater":
        return np.greater(a, b)
    elif op_str == "GreaterEq":
        return np.greater_equal(a, b)
    elif op_str == "Less":
        return np.less(a, b)
    elif op_str == "LessEq":
        return np.less_equal(a, b)
    elif op_str == "Maximum":
        return np.maximum(a, b)
    elif op_str == "Minimum":
        return np.minimum(a, b)
    elif op_str == "NotEqual":
        return np.not_equal(a, b)
    elif op_str == "Power":
        return np.power(a, b)


def binary_op_exec(op_str):

    element_type = Type.f32
    shape = [2,2]
    A = Parameter(element_type, shape)
    B = Parameter(element_type, shape)
    parameter_list = [A, B]
    function = Function([binary_op(op_str, A, B)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    b = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(element_type, shape)

    a.write(util.numpy_to_c(np.array([[1,6],[7,4]], dtype=np.float32)), 0, 16)
    b.write(util.numpy_to_c(np.array([[5,2],[3,8]], dtype=np.float32)), 0, 16)

    result_arr = np.array([[0, 0], [0, 0]], dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 16)
    cf.call([a, b], [result])
    result.read(util.numpy_to_c(result_arr), 0, 16)

    a_arr = np.array([[1, 6], [7, 4]], dtype=np.float32)
    b_arr = np.array([[5, 2], [3, 8]], dtype=np.float32)
    result_arr_ref = binary_op_ref(op_str, a_arr, b_arr)

    assert np.allclose(result_arr, result_arr_ref)


def binary_op_comparison(op_str):

    element_type = Type.f32
    shape = [2, 2]
    A = Parameter(element_type, shape)
    B = Parameter(element_type, shape)
    parameter_list = [A, B]
    function = Function([binary_op(op_str, A,  B)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    b = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(Type.boolean, shape)

    a.write(util.numpy_to_c(np.array([[1, 5], [3, 2]], dtype=np.float32)), 0, 16)
    b.write(util.numpy_to_c(np.array([[2, 4], [3, 1]], dtype=np.float32)), 0, 16)

    result_arr = np.array([[False, False], [False, False]], dtype=np.bool)
    result.write(util.numpy_to_c(result_arr), 0, 4)
    cf.call([a, b], [result])
    result.read(util.numpy_to_c(result_arr), 0, 4)

    a_arr = np.array([[1, 5], [3, 2]], dtype=np.float32)
    b_arr = np.array([[2, 4], [3, 1]], dtype=np.float32)
    result_arr_ref = binary_op_ref(op_str, a_arr, b_arr)

    assert np.allclose(result_arr, result_arr_ref)


def test_add():
    binary_op_exec("+")


def test_add_op():
    binary_op_exec("Add")


def test_sub():
    binary_op_exec("-")


def test_sub_op():
    binary_op_exec("Sub")


def test_mul():
    binary_op_exec("*")


def test_mul_op():
    binary_op_exec("Mul")


def test_div():
    binary_op_exec("/")


def test_div_op():
    binary_op_exec("Div")


def test_dot():
    binary_op_exec("Dot")


def test_maximum():
    binary_op_exec("Maximum")


def test_minimum():
    binary_op_exec("Minimum")


def test_power():
    binary_op_exec("Power")


def test_greater():
    binary_op_comparison("Greater")


def test_greater_eq():
    binary_op_comparison("GreaterEq")


def test_less():
    binary_op_comparison("Less")


def test_less_eq():
    binary_op_comparison("LessEq")


def test_not_equal():
    binary_op_comparison("NotEqual")


def test_add_with_mul():

    element_type = Type.f32
    shape = [2,2]
    A = Parameter(element_type, shape)
    B = Parameter(element_type, shape)
    C = Parameter(element_type, shape)
    parameter_list = [A, B, C]
    function = Function([Multiply(Add(A,  B), C)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    b = backend.make_primary_tensor_view(element_type, shape)
    c = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(element_type, shape)

    a.write(util.numpy_to_c(np.array([1,2,3,4], dtype=np.float32)), 0, 16)
    b.write(util.numpy_to_c(np.array([5,6,7,8], dtype=np.float32)), 0, 16)
    c.write(util.numpy_to_c(np.array([9,10,11,12], dtype=np.float32)), 0, 16)

    result_arr = np.array([0, 0, 0, 0], dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 16)
    cf.call([a, b, c], [result])
    result.read(util.numpy_to_c(result_arr), 0, 16)

    a_arr = np.array([1, 2, 3, 4], dtype=np.float32)
    b_arr = np.array([5, 6, 7, 8], dtype=np.float32)
    c_arr = np.array([9, 10, 11, 12], dtype=np.float32)
    result_arr_ref = (a_arr + b_arr) * c_arr

    assert np.allclose(result_arr, result_arr_ref)


def unary_op(op_str, a):
    if op_str == 'Abs':
        return Abs(a)
    elif op_str == 'Acos':
        return Acos(a)
    elif op_str == 'Asin':
        return Asin(a)
    elif op_str == 'Atan':
        return Atan(a)
    elif op_str == 'Ceiling':
        return Ceiling(a)
    elif op_str == 'Cos':
        return Cos(a)
    elif op_str == 'Cosh':
        return Cosh(a)
    elif op_str == 'Floor':
        return Floor(a)
    elif op_str == 'log':
        return Log(a)
    elif op_str == 'exp':
        return Exp(a)
    elif op_str == 'negative':
        return Negative(a)
    elif op_str == 'Reverse':
        return Reverse(a, {0})
    elif op_str == 'Sign':
        return Sign(a)
    elif op_str == 'Sin':
        return Sin(a)
    elif op_str == 'Sinh':
        return Sinh(a)
    elif op_str == 'Sqrt':
        return Sqrt(a)
    elif op_str == 'Tan':
        return Tan(a)
    elif op_str == 'Tanh':
        return Tanh(a)


def unary_op_ref(op_str, a):
    if op_str == 'Abs':
        return np.abs(a)
    elif op_str == 'Acos':
        return np.arccos(a)
    elif op_str == 'Asin':
        return np.arcsin(a)
    elif op_str == 'Atan':
        return np.arctan(a)
    elif op_str == 'Ceiling':
        return np.ceil(a)
    elif op_str == 'Cos':
        return np.cos(a)
    elif op_str == 'Cosh':
        return np.cosh(a)
    elif op_str == 'Floor':
        return np.floor(a)
    elif op_str == 'log':
        return np.log(a)
    elif op_str == 'exp':
        return np.exp(a)
    elif op_str == 'negative':
        return np.negative(a)
    elif op_str == 'Reverse':
        return np.fliplr(a)
    elif op_str == 'Sign':
        return np.sign(a)
    elif op_str == 'Sin':
        return np.sin(a)
    elif op_str == 'Sinh':
        return np.sinh(a)
    elif op_str == 'Sqrt':
        return np.sqrt(a)
    elif op_str == 'Tan':
        return np.tan(a)
    elif op_str == 'Tanh':
        return np.tanh(a)


def unary_op_exec(op_str, input_list):

    """
    input_list needs to have deep length of 4
    """
    element_type = Type.f32
    shape = [2,2]
    A = Parameter(element_type, shape)
    parameter_list = [A]
    function = Function([unary_op(op_str, A)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(element_type, shape)

    a.write(util.numpy_to_c(np.array(input_list, dtype=np.float32)), 0, 16)

    result_arr = np.array([0, 0, 0, 0], dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 16)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 16)

    a_arr = np.array(input_list, dtype=np.float32)
    result_arr_ref = unary_op_ref(op_str, a_arr)

    assert np.allclose(result_arr, result_arr_ref)


def test_abs():
    input_list = [-1, 0, 1, 2]
    op_str = 'Abs'
    unary_op_exec(op_str, input_list)


def test_acos():
    input_list = [-1, 0, 0.5, 1]
    op_str = 'Acos'
    unary_op_exec(op_str, input_list)


def test_asin():
    input_list = [-1, 0, 0.5, 1]
    op_str = 'Asin'
    unary_op_exec(op_str, input_list)


def test_atan():
    input_list = [-1, 0, 0.5, 1]
    op_str = 'Atan'
    unary_op_exec(op_str, input_list)


def test_ceiling():
    input_list = [0.5, 0, 0.4, 0.5]
    op_str = 'Ceiling'
    unary_op_exec(op_str, input_list)


def test_cos():
    input_list = [0, 0.7, 1.7, 3.4]
    op_str = 'Cos'
    unary_op_exec(op_str, input_list)


def test_cosh():
    input_list = [-1, 0., 0.5, 1]
    op_str = 'Cosh'
    unary_op_exec(op_str, input_list)


def test_floor():
    input_list = [-0.5, 0, 0.4, 0.5]
    op_str = 'Floor'
    unary_op_exec(op_str, input_list)


def test_log():
    input_list = [1, 2, 3, 4]
    op_str = 'log'
    unary_op_exec(op_str, input_list)


def test_exp():
    input_list = [-1, 0, 1, 2]
    op_str = 'exp'
    unary_op_exec(op_str, input_list)


def test_negative():
    input_list = [-1, 0, 1, 2]
    op_str = 'negative'
    unary_op_exec(op_str, input_list)


def test_sign():
    input_list = [-1, 0, 0.5,  1]
    op_str = 'Sign'
    unary_op_exec(op_str, input_list)


def test_sin():
    input_list = [0, 0.7, 1.7, 3.4]
    op_str = 'Sin'
    unary_op_exec(op_str, input_list)


def test_sinh():
    input_list = [-1, 0., 0.5, 1]
    op_str = 'Sinh'
    unary_op_exec(op_str, input_list)


def test_sqrt():
    input_list = [0., 0.5, 1, 2]
    op_str = 'Sqrt'
    unary_op_exec(op_str, input_list)


def test_tan():
    input_list = [-np.pi/4, 0, np.pi/8, np.pi/8]
    op_str = 'Tan'
    unary_op_exec(op_str, input_list)


def test_tanh():
    input_list = [-1, 0, 0.5, 1]
    op_str = 'Tanh'
    unary_op_exec(op_str, input_list)


def test_reverse():
    return
    input_list = [[-1, 0], [0.5, 1]]
    op_str = 'Reverse'
    unary_op_exec(op_str, input_list)


def test_not():
    element_type = Type.boolean
    shape = [2]
    A = Parameter(element_type, shape)
    parameter_list = [A]
    function = Function([Not(A)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    b = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(Type.boolean, shape)

    a.write(util.numpy_to_c(np.array([True, False], dtype=np.bool)), 0, 2)

    result_arr = np.array([False, False], dtype=np.bool)
    result.write(util.numpy_to_c(result_arr), 0, 2)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 2)

    a_arr = np.array([True, False], dtype=np.bool)
    result_arr_ref = np.logical_not(a_arr)

    assert np.allclose(result_arr, result_arr_ref)


def test_sum():

    element_type = Type.f32
    shape = [1, 4]
    A = Parameter(element_type, shape)
    parameter_list = [A]
    function = Function([Sum(A, {1})], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(element_type, [1])

    a.write(util.numpy_to_c(np.array([1, 2, 3, 4], dtype=np.float32)), 0, 16)

    result_arr = np.array([0], dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 4)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 4)

    a_arr = np.array([1, 2, 3, 4], dtype=np.float32)
    result_arr_ref = np.sum(a_arr)

    assert np.allclose(result_arr[0], result_arr_ref)


def test_reshape():

    element_type = Type.f32
    shape = [2,3]
    A = Parameter(element_type, shape)
    parameter_list = [A]
    function = Function([Reshape(A,  [0, 1], [3, 2])], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(element_type, [3, 2])

    a.write(util.numpy_to_c(np.array([[1,2,3],[4,5,6]], dtype=np.float32)), 0, 24)

    result_arr = np.array([[0, 0], [0, 0], [0, 0]], dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 24)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 24)

    a_arr = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
    result_arr_ref = np.reshape(a_arr, (3, 2))

    assert np.allclose(result_arr, result_arr_ref)


def test_convert():

    element_type = Type.f32
    shape = [1,3]
    A = Parameter(element_type, shape)
    parameter_list = [A]
    #f32 to boolean
    function = Function([Convert(A, Type.boolean)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(Type.boolean, shape)

    a.write(util.numpy_to_c(np.array([1, 5, 3], dtype=np.float32)), 0, 12)

    result_arr = np.array([False, False, False], dtype=np.bool)
    result.write(util.numpy_to_c(result_arr), 0, 3)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 3)

    a_arr = np.array([1, 5, 3], dtype=np.float32)
    result_arr_ref = a_arr.astype(bool)
    assert np.allclose(result_arr, result_arr_ref)

    #f32 to i32
    function = Function([Convert(A, Type.i32)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    result = backend.make_primary_tensor_view(Type.i32, shape)

    a.write(util.numpy_to_c(np.array([1.4, 5.5, 3.9], dtype=np.float32)), 0, 12)

    result_arr = np.array([0, 0, 0], dtype=np.int32)
    result.write(util.numpy_to_c(result_arr), 0, 12)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 12)

    a_arr = np.array([1.4, 5.4, 3.9], dtype=np.float32)
    result_arr_ref = a_arr.astype(int)

    assert np.allclose(result_arr, result_arr_ref)


def test_broadcast():

    element_type = Type.f32
    A = Parameter(element_type, [3])
    parameter_list = [A]
    function = Function([Broadcast(A, [3, 3], {0})], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, [3])
    result = backend.make_primary_tensor_view(element_type, [3,3])

    a.write(util.numpy_to_c(np.array([1,2,3], dtype=np.float32)), 0, 12)

    result_arr = np.zeros((3,3), dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 36)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 36)

    a_arr = np.array([[0],[0],[0]], dtype=np.float32)
    b_arr = np.array([[1, 2, 3]], dtype=np.float32)
    result_arr_ref = np.add(a_arr, b_arr)

    assert np.allclose(result_arr, result_arr_ref)


def test_constant():

    element_type = Type.f32
    parameter_list = []
    function = Function([Constant(element_type, [3,3], list(range(9)))],
                                 parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    result = backend.make_primary_tensor_view(element_type, [3,3])

    result_arr = np.zeros((3,3), dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 36)
    cf.call([], [result])
    result.read(util.numpy_to_c(result_arr), 0, 36)

    result_arr_ref = np.arange(9).reshape(3,3)

    assert np.allclose(result_arr, result_arr_ref)


def test_reduce():

    float_element_type = Type.f32

    AddParam1 = Parameter(float_element_type, [])
    AddParam2 = Parameter(float_element_type, [])
    constant_op = Constant(float_element_type, [], [0.])
    reduce_function = Function([Add(AddParam1, AddParam2)],
                                        [AddParam1, AddParam2], 'add')

    A = Parameter(float_element_type, [2, 2, 2])
    parameter_list = [A]

    function = Function([Reduce(A, constant_op, reduce_function, {0})],
                                 parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(float_element_type, [2, 2, 2])
    result = backend.make_primary_tensor_view(float_element_type, [2,2])

    a.write(util.numpy_to_c(np.arange(8, dtype=np.float32).reshape(2,2,2)), 0, 32)

    result_arr = np.zeros((2,2), dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 16)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 16)

    a_arr = np.arange(8).reshape(2,2,2)
    result_arr_ref = np.add.reduce(a_arr)

    assert np.allclose(result_arr, result_arr_ref)


def test_onehot():

    element_type = Type.f32
    A = Parameter(element_type, [3])
    parameter_list = [A]
    function = Function([OneHot(A, [3, 3], 0)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, [3])
    result = backend.make_primary_tensor_view(element_type, [3,3])

    a.write(util.numpy_to_c(np.array([1,0,2], dtype=np.float32)), 0, 12)

    result_arr = np.zeros((3,3), dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 36)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 36)

    a_arr = np.array([1,0,2])
    result_arr_ref = np.eye(3)[a_arr]

    assert np.allclose(result_arr, result_arr_ref)


def test_concat():

    element_type = Type.f32
    A = Parameter(element_type, [1, 2])
    B = Parameter(element_type, [1, 2])
    C = Parameter(element_type, [1, 2])
    parameter_list = [A, B, C]
    axis = 0
    function = Function([Concat([A,  B, C], axis)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, [1, 2])
    b = backend.make_primary_tensor_view(element_type, [1, 2])
    c = backend.make_primary_tensor_view(element_type, [1, 2])
    result = backend.make_primary_tensor_view(element_type, [3, 2])

    a.write(util.numpy_to_c(np.array([1,2], dtype=np.float32)), 0, 8)
    b.write(util.numpy_to_c(np.array([5,6], dtype=np.float32)), 0, 8)
    c.write(util.numpy_to_c(np.array([7,8], dtype=np.float32)), 0, 8)

    result_arr = np.zeros(6, dtype=np.float32).reshape(3, 2)
    result.write(util.numpy_to_c(result_arr), 0, 24)
    cf.call([a, b, c], [result])
    result.read(util.numpy_to_c(result_arr), 0, 24)

    a_arr = np.array([[1, 2]], dtype=np.float32)
    b_arr = np.array([[5, 6]], dtype=np.float32)
    c_arr = np.array([[7, 8]], dtype=np.float32)
    result_arr_ref = np.concatenate((a_arr, b_arr, c_arr), axis)

    assert np.allclose(result_arr, result_arr_ref)


def test_select():

    element_type = Type.f32
    A = Parameter(Type.boolean, [1, 2])
    B = Parameter(element_type, [1, 2])
    C = Parameter(element_type, [1, 2])
    parameter_list = [A, B, C]

    function = Function([Select(A,  B, C)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(Type.boolean, [1, 2])
    b = backend.make_primary_tensor_view(element_type, [1, 2])
    c = backend.make_primary_tensor_view(element_type, [1, 2])
    result = backend.make_primary_tensor_view(element_type, [1, 2])

    a.write(util.numpy_to_c(np.array([[True, False]], dtype=np.bool)), 0, 2)
    b.write(util.numpy_to_c(np.array([[5,6]], dtype=np.float32)), 0, 8)
    c.write(util.numpy_to_c(np.array([[7,8]], dtype=np.float32)), 0, 8)

    result_arr = np.array([[0, 0]], dtype=np.float32)
    result.write(util.numpy_to_c(result_arr), 0, 8)
    cf.call([a, b, c], [result])
    result.read(util.numpy_to_c(result_arr), 0, 8)

    result_arr_ref = np.array([[5,8]])

    assert np.allclose(result_arr, result_arr_ref)


def test_slice():

    element_type = Type.f32
    shape = [6,6]
    A = Parameter(element_type, shape)
    parameter_list = [A]

    input_arr = np.arange(36, dtype=np.float32).reshape(6,6)
    lower_bounds = [1, 1]
    upper_bounds = [5, 5]

    function = Function([Slice(A,  lower_bounds, upper_bounds)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    a = backend.make_primary_tensor_view(element_type, shape)
    result = backend.make_primary_tensor_view(element_type, [4, 4])

    a.write(util.numpy_to_c(input_arr), 0, 36*4)

    result_arr = np.zeros(16, dtype=np.float32).reshape(4, 4)
    result.write(util.numpy_to_c(result_arr), 0, 16*4)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 64)

    result_arr_ref = input_arr[lower_bounds[0]:upper_bounds[1], lower_bounds[0]:upper_bounds[1]]

    assert np.allclose(result_arr, result_arr_ref)


    #test with strides
    strides = [1, 2]

    function = Function([Slice(A,  lower_bounds, upper_bounds, strides)], parameter_list, 'test')
    backend, cf = make_backend_call_frame(function)

    result = backend.make_primary_tensor_view(element_type, [4, 2])
    result_arr = np.zeros(8, dtype=np.float32).reshape(4, 2)

    result.write(util.numpy_to_c(result_arr), 0, 8*4)
    cf.call([a], [result])
    result.read(util.numpy_to_c(result_arr), 0, 32)

    result_arr_ref = result_arr_ref[::strides[0], ::strides[1]]

    assert np.allclose(result_arr, result_arr_ref)



