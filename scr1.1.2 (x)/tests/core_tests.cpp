#include "rdfw.hpp"
#include <cassert>
#include <type_traits>
#include <sstream>
#include <iostream>
using namespace _home;

static_assert(!std::is_convertible<ObjectId, LocationId>::value, "ID domains must differ");
static_assert(!std::is_convertible<LocationId, ObjectId>::value, "ID domains must differ");
static_assert(!std::is_convertible<int, ObjectId>::value, "raw IDs require an explicit adapter");

int main(int argc, char** argv) {
    assert(argc == 2);
    ObjectObjectTable oo(3, ObjectVector<int>(3, 0));
    ObjectLocationTable ol(3, LocationVector<int>(8, 0));
    oo[ObjectId(2)][ObjectId(1)] = 7;
    ol[ObjectId(2)][LocationId(6)] = 9;
    assert(oo[ObjectId(2)][ObjectId(1)] == 7);
    bool rejected = false;
    try { ol[ObjectId(2)][LocationId(-1)] = 1; }
    catch (const std::out_of_range&) { rejected = true; }
    assert(rejected);

    TimeBudget budget;
    budget.configure(100, 20);
    assert(budget.phase_at(79) == TimeBudget::Phase::Normal);
    assert(budget.phase_at(80) == TimeBudget::Phase::Finishing);
    assert(budget.phase_at(99) == TimeBudget::Phase::Finishing);
    assert(budget.phase_at(100) == TimeBudget::Phase::Expired);
    budget.configure(0, 0);
    assert(budget.phase_at(100000) == TimeBudget::Phase::Normal);
    rejected = false;
    try { budget.configure(10, 10); } catch (const std::invalid_argument&) { rejected = true; }
    assert(rejected);

    SmallObject small(7, 903, "cup", "red");
    BigObject big(2, 900, "desk");
    assert(small.id == 7 && small.location == 903);
    assert(big.id == 2 && big.location == 900);

    auto world = std::make_shared<RDFW>();
    char name[] = "core_tests", path_arg[] = "-path";
    char* init_args[] = {name, path_arg, argv[1]};
    world->Init(3, init_args);
    // Object IDs and locations deliberately occupy different ranges.
    assert(world->ParseEnv(" (hold 0) (plate 0) (at 0 903) "
                          "(sort 1 human) (size 1 big) (at 1 900) "
                          "(sort 2 desk) (size 2 big) (at 2 901) "
                          "(sort 3 cup) (size 3 small) (color 3 red)"));
    assert(world->open_cons.size() == 100); // a large location did not grow object tables
    assert(world->goto_cons.size() == 904);
    assert(world->move_cons.size() == 100);
    assert(world->move_cons[ObjectId(3)].size() == 904);
    const auto location_count = world->goto_cons.size();
    assert(world->ParseEnv(" (sort 120 book) (size 120 small) (color 120 blue) (at 120 901)"));
    assert(world->open_cons.size() == 121);
    assert(world->goto_cons.size() == location_count); // a large object ID did not grow locations
    assert(world->putin_cons[ObjectId(120)].size() == 121);
    assert(world->move_cons[ObjectId(120)].size() == 904);

    Instruction unknown;
    unknown.behave = "goto";
    unknown.X.push_back(world->objects[ObjectId(3)]);
    assert(world->CalculateTaskRisk(unknown) == 0); // UNKNOWN never becomes vector[-1]
    world->tasks.push_back(unknown);
    Instruction pickup = unknown;
    pickup.behave = "pickup";
    world->tasks.push_back(pickup);
    world->tasks = world->TaskOptimization();
    assert(world->pickup[ObjectId(3)]); // no dangling pointer after task vector replacement
    world->Fini();
    assert(!world->pickup[ObjectId(3)]);
    assert(world->budget.phase() == TimeBudget::Phase::Normal);
    std::cout << "core tests passed\n";
}
