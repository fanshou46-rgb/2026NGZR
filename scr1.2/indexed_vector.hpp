#pragma once
#include <vector>
#include <stdexcept>
#include <cstddef>

namespace _home {
// No implicit conversion in either direction, including ObjectId <-> LocationId.
template<class Tag> class Index {
    int value_;
public:
    explicit Index(int value) : value_(value) {}
    int value() const { return value_; }
};
struct ObjectTag {};
struct LocationTag {};
typedef Index<ObjectTag> ObjectId;
typedef Index<LocationTag> LocationId;

// Keep vector iteration/reset support while requiring a domain at every lookup.
// Invalid/sentinel indices fail before touching memory; callers handle UNKNOWN.
template<class Key, class Value> class IndexedVector : public std::vector<Value> {
    typedef std::vector<Value> Base;
public:
    using Base::Base;
    IndexedVector() : Base() {}
    IndexedVector(const Base& values) : Base(values) {}
    typename Base::reference operator[](Key key) {
        if (key.value() < 0) throw std::out_of_range("negative domain index");
        return Base::at(static_cast<std::size_t>(key.value()));
    }
    typename Base::const_reference operator[](Key key) const {
        if (key.value() < 0) throw std::out_of_range("negative domain index");
        return Base::at(static_cast<std::size_t>(key.value()));
    }
};
template<class T> using ObjectVector = IndexedVector<ObjectId, T>;
template<class T> using LocationVector = IndexedVector<LocationId, T>;
typedef ObjectVector<ObjectVector<int> > ObjectObjectTable;
typedef ObjectVector<LocationVector<int> > ObjectLocationTable;
}
