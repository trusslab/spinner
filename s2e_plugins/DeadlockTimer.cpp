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
#include <s2e/Utils.h>
#include <timer.h>
#include <s2e/cpu.h>
#include <sys/types.h>
#include <unordered_map>

#include <s2e/Plugins/OSMonitors/Linux/LinuxMonitor.h>
#include <s2e/Plugins/ExecutionTracers/TestCaseGenerator.h>


#include "DeadlockTimer.h"

namespace s2e {
namespace plugins {

namespace {

//
// This class can optionally be used to store per-state plugin data.
//
// Use it as follows:
// void DeadlockTimer::onEvent(S2EExecutionState *state, ...) {
//     DECLARE_PLUGINSTATE(DeadlockTimerState, state);
//     plgState->...
// }
//
class DeadlockTimerState: public PluginState {
    // Declare any methods and fields you need here
private:
    std::unordered_map<uint64_t, pid_t> lockOwners;
    bool tracking;
public:
    DeadlockTimerState() {
	    tracking = false;
    }

    static PluginState *factory(Plugin *p, S2EExecutionState *s) {
        return new DeadlockTimerState();
    }
    virtual ~DeadlockTimerState() {
        // Destroy any object if needed
    }
    virtual DeadlockTimerState *clone() const {
        return new DeadlockTimerState(*this);
    }

    void start_tracking() {
	    tracking = true;
    }

    bool get_tracking() {
	    return tracking;
    }

    pid_t get_owner(uint64_t lockAddress) {
	auto it = lockOwners.find(lockAddress);
	return (it != lockOwners.end()) ? it->second : -1;
    }

    void insert_owner(uint64_t lockAddress, pid_t threadID) {
	    lockOwners[lockAddress] = threadID;
    }

    void delete_owner(uint64_t lockAddress) {
	    lockOwners.erase(lockAddress);
    }
};

}

S2E_DEFINE_PLUGIN(DeadlockTimer, "Detects and prevents recursive deadlock", "DeadlockTimer", "LinuxMonitor", "TestCaseGenerator" );

void DeadlockTimer::initialize() {
	m_address_start = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".startAddress");
	
	m_address_irqsave_lock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".irqsaveLockAddress");
	m_address_irqrestore_unlock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".irqrestoreUnlockAddress");

	m_address_irq_lock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".irqLockAddress");
        m_address_irq_unlock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".irqUnlockAddress");

	m_address_bh_lock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".bhLockAddress");
        m_address_bh_unlock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".bhUnlockAddress");
	
	m_address_lock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".lockAddress");
        m_address_unlock = (uint64_t) s2e()->getConfig()->getInt(getConfigKey() + ".unlockAddress");
	
	s2e()->getCorePlugin()->onTranslateInstructionStart.connect(sigc::mem_fun(*this, &DeadlockTimer::onTranslateInstruction));
}


void DeadlockTimer::onTranslateInstruction(ExecutionSignal *signal, S2EExecutionState *state, TranslationBlock *tb, uint64_t pc) {
	if ((m_address_start == pc) || (m_address_irqsave_lock == pc) || (m_address_irqrestore_unlock == pc) || (m_address_irq_lock == pc) || (m_address_irq_unlock == pc) || (m_address_bh_lock == pc) || (m_address_bh_unlock == pc) || (m_address_lock == pc) || (m_address_unlock == pc)) {
		signal->connect(sigc::mem_fun(*this, &DeadlockTimer::onInstructionExecution));
	}
}

void DeadlockTimer::onInstructionExecution(S2EExecutionState *state, uint64_t pc) {
	LinuxMonitor *m_monitor = (s2e()->getPlugin<LinuxMonitor>());
	pid_t thread_id = m_monitor->getTid(state);
        //uint64_t lock_addr = static_cast<uint64_t>(state->regs()->read<target_ulong>(CPU_OFFSET(regs[R_EDI])));
	uint64_t lock_addr = (state->regs()->read<target_ulong>(offsetof(CPUX86State, regs[R_EDI])));
	testcases::TestCaseGenerator *generator = s2e()->getPlugin<testcases::TestCaseGenerator>();

	DECLARE_PLUGINSTATE(DeadlockTimerState, state);
	//s2e()->getDebugStream() <<"Lock at "<<hexval(lock_addr)<<" taken by thread "<<thread_id<<"\n";
	if (pc == m_address_start) {
		plgState->start_tracking();
	}

	if (((pc == m_address_irqsave_lock) || (pc == m_address_irq_lock) || (pc == m_address_bh_lock) || (pc == m_address_lock) ) && plgState->get_tracking()) {
        	if (plgState->get_owner(lock_addr) == thread_id) {
            		s2e()->getDebugStream(state) << "Deadlock detected! Thread " << thread_id<< " re-acquired lock " << hexval(lock_addr) << "\n";
            	        generator->generateTestCases(state, "deadlock", testcases::TC_TRACE);
			s2e()->getExecutor()->terminateState(*state, "Self-deadlock detected");
        	}
		else {
        		plgState->insert_owner(lock_addr, thread_id);
		}
	}

	else if (((pc ==m_address_irqrestore_unlock) || (pc ==m_address_irq_unlock) || (pc ==m_address_bh_unlock) || (pc ==m_address_unlock) ) && plgState->get_tracking()) {
		plgState->delete_owner(lock_addr);
		//s2e()->getDebugStream(state) <<"Thread "<<thread_id<<" released lock "<<hexval(lock_addr)<<"\n";
	}
	
}

void DeadlockTimer::handleOpcodeInvocation(S2EExecutionState *state, uint64_t guestDataPtr, uint64_t guestDataSize)
{
    S2E_DEADLOCKTIMER_COMMAND command;

    if (guestDataSize != sizeof(command)) {
        getWarningsStream(state) << "mismatched S2E_DEADLOCKTIMER_COMMAND size\n";
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
