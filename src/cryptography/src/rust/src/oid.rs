// This file is dual licensed under the terms of the Apache License, Version
// 2.0, and the BSD License. See the LICENSE file in the root of this repository
// for complete details.

use crate::asn1::PyAsn1Result;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

#[pyo3::prelude::pyclass]
pub(crate) struct ObjectIdentifier {
    pub(crate) oid: asn1::ObjectIdentifier,
}

#[pyo3::pymethods]
impl ObjectIdentifier {
    #[new]
    fn new(value: &str) -> PyAsn1Result<Self> {
        let oid = asn1::ObjectIdentifier::from_string(value)
            .ok_or_else(|| asn1::ParseError::new(asn1::ParseErrorKind::InvalidValue))?;
        Ok(ObjectIdentifier { oid })
    }

    #[getter]
    fn dotted_string<'p>(&self, py: pyo3::Python<'p>) -> &'p pyo3::types::PyString {
        pyo3::types::PyString::new(py, &self.oid.to_string())
    }

    #[getter]
    fn _name<'p>(
        slf: pyo3::PyRef<'_, Self>,
        py: pyo3::Python<'p>,
    ) -> pyo3::PyResult<&'p pyo3::PyAny> {
        let oid_names = py
            .import("cryptography.hazmat._oid")?
            .getattr(crate::intern!(py, "_OID_NAMES"))?;
        oid_names.call_method1("get", (slf, "Unknown OID"))
    }

    fn __deepcopy__(slf: pyo3::PyRef<'_, Self>, _memo: pyo3::PyObject) -> pyo3::PyRef<'_, Self> {
        slf
    }
}

#[pyo3::prelude::pyproto]
impl pyo3::PyObjectProtocol for ObjectIdentifier {
    fn __repr__(&self) -> pyo3::PyResult<String> {
        let gil = pyo3::Python::acquire_gil();
        let py = gil.python();

        let self_clone = pyo3::PyCell::new(
            py,
            ObjectIdentifier {
                oid: self.oid.clone(),
            },
        )?;
        let name = ObjectIdentifier::_name(self_clone.borrow(), py)?.extract::<&str>()?;
        Ok(format!(
            "<ObjectIdentifier(oid={}, name={})>",
            self.oid, name
        ))
    }

    fn __richcmp__(
        &self,
        other: pyo3::PyRef<ObjectIdentifier>,
        op: pyo3::basic::CompareOp,
    ) -> pyo3::PyResult<bool> {
        match op {
            pyo3::basic::CompareOp::Eq => Ok(self.oid == other.oid),
            pyo3::basic::CompareOp::Ne => Ok(self.oid != other.oid),
            _ => Err(pyo3::exceptions::PyTypeError::new_err(
                "ObjectIdentifiers cannot be ordered",
            )),
        }
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.oid.hash(&mut hasher);
        hasher.finish()
    }
}
