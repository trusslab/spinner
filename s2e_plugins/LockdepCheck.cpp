///
/// Copyright (C) 2025, PriyaBG313
///
/// Permission is hereby granted, free of charge, to any person obtaining a copy
/// of this software and associated documentation files (the "Software"), to deal
/// in the Software without restriction, including without limitation the rights
/// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
/// copies of the Software, and to permit persons to whom the Software is
/// furnished to do so, subject to the following conditions:
///
/// The above copyright notice and this permission notice shall be included in all
/// copies or substantial portions of the Software.
///
/// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
/// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
/// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
/// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
/// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
/// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
/// SOFTWARE.
///

#include <s2e/S2E.h>
#include <s2e/ConfigFile.h>

#include <s2e/Plugins/ExecutionTracers/TestCaseGenerator.h>

#include "LockdepCheck.h"

namespace s2e {
namespace plugins {

namespace {

//
// This class can optionally be used to store per-state plugin data.
//
// Use it as follows:
// void LockdepCheck::onEvent(S2EExecutionState *state, ...) {
//     DECLARE_PLUGINSTATE(LockdepCheckState, state);
//     plgState->...
// }
//
class LockdepCheckState: public PluginState {
    // Declare any methods and fields you need here

public:
    static PluginState *factory(Plugin *p, S2EExecutionState *s) {
        return new LockdepCheckState();
    }

    virtual ~LockdepCheckState() {
        // Destroy any object if needed
    }

    virtual LockdepCheckState *clone() const {
        return new LockdepCheckState(*this);
    }
};

}

S2E_DEFINE_PLUGIN(LockdepCheck, "Generates test cases once lockdep prints a report", "LockdepCheck", "TestCaseGenerator");

void LockdepCheck::initialize() {
    m_address = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".lockdepUsageBugAddress");
    m_address2 = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".lockdepInvalidWaitAddress");
    s2e()->getDebugStream()<<"TriggerBPF: Tracking address "<<hexval(m_address)<<"\n";
    s2e()->getCorePlugin()->onTranslateInstructionStart.connect(sigc::mem_fun(*this, &LockdepCheck::onTranslateInstruction));
}

void LockdepCheck::onTranslateInstruction(ExecutionSignal *signal, S2EExecutionState *state, TranslationBlock *tb, uint64_t pc)
{

    //if (m_address == pc || m_address2 == pc) {
    if (m_address == pc) {
        signal->connect(sigc::mem_fun(*this, &LockdepCheck::onInstructionExecution));
    }

}

void LockdepCheck::onInstructionExecution(S2EExecutionState *state, uint64_t pc)
{
	if (m_address==pc) {
        	s2e()->getDebugStream()<< "LockdepCheck: Address "<<hexval(m_address)<<" reached.\n";
        	testcases::TestCaseGenerator *generator = s2e()->getPlugin<testcases::TestCaseGenerator>();
        	generator->generateTestCases(state, "deadlock", testcases::TC_TRACE);
		//s2e()->getExecutor()->terminateState(*state, "Lockdep detected deadlock");
	}/*
	else {
		s2e()->getDebugStream()<< "LockdepCheck: Address of Invalid Wait "<<hexval(m_address)<<" reached.\n";
		s2e()->getExecutor()->terminateState(*state, "Lockdep detected invalid wait");
	}
	*/
}


void LockdepCheck::handleOpcodeInvocation(S2EExecutionState *state, uint64_t guestDataPtr, uint64_t guestDataSize)
{
    S2E_LOCKDEPCHECK_COMMAND command;

    if (guestDataSize != sizeof(command)) {
        getWarningsStream(state) << "mismatched S2E_LOCKDEPCHECK_COMMAND size\n";
        return;
    }

    if (!state->mem()->read(guestDataPtr, &command, guestDataSize)) {
        getWarningsStream(state) << "could not read transmitted data\n";
        return;
    }

    switch (command.Command) {
        // TODO: add custom commands here
        case COMMAND_1:
            break;
        default:
            getWarningsStream(state) << "Unknown command " << command.Command << "\n";
            break;
    }
}



} // namespace plugins
} // namespace s2e
