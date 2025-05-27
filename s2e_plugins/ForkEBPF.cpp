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


#include "ForkEBPF.h"

namespace s2e {
namespace plugins {

namespace {

//
// This class can optionally be used to store per-state plugin data.
//
// Use it as follows:
// void ForkEBPF::onEvent(S2EExecutionState *state, ...) {
//     DECLARE_PLUGINSTATE(ForkEBPFState, state);
//     plgState->...
// }
//
class ForkEBPFState: public PluginState {
    // Declare any methods and fields you need here
private:
	int m_count;

public:

	ForkEBPFState() {
		m_count = 0;
	}

    static PluginState *factory(Plugin *p, S2EExecutionState *s) {
        return new ForkEBPFState();
    }

    virtual ~ForkEBPFState() {
        // Destroy any object if needed
    }

    virtual ForkEBPFState *clone() const {
        return new ForkEBPFState(*this);
    }

    void increment() { ++m_count; }
    int get() { return m_count; }
};

}

S2E_DEFINE_PLUGIN(ForkEBPF, "Decides whether to Fork or not based on current PC", "", );

void ForkEBPF::initialize() {
	s2e()->getCorePlugin()->onStateForkDecide.connect(sigc::mem_fun(*this, &ForkEBPF::onStateForkDecide));
}

void ForkEBPF::onStateForkDecide(S2EExecutionState *state, const klee::ref<klee::Expr> &condition, bool &allowForking) {
	uint64_t curPc = state->regs()->getPc();
	DECLARE_PLUGINSTATE(ForkEBPFState, state);

	std::string resolvedInfo = ForkEBPF::resolveAddress(curPc);
        if (resolvedInfo.find("kernel/bpf") == std::string::npos || resolvedInfo.find("bpf_jit_comp") != std::string::npos) {
		allowForking=false;
		/*
		if (s2e_is_running_concrete()) {
			state->switchToSymbolic();
		}
		*/
		
		if (resolvedInfo.find("kernel/module/main.c:3282")!=std::string::npos) {
			
			plgState->increment();
			if (plgState->get()>5){
			;//	s2e()->getExecutor()->terminateState(*state, "recurring path");
			}
			//print_stacktrace(s2e_warning_print, "Recurring path");
		}
		
        }
	
	s2e()->getDebugStream(state) << "on state fork decide "<< resolvedInfo ;
}

std::string ForkEBPF::resolveAddress(uint64_t addr) {
    std::ostringstream command;
    command << "addr2line -e ~/s2e/images/debian-12.5-x86_64/guestfs/vmlinux " << (hexval(addr)) << " > /tmp/addr2line_output.txt 2>/dev/null";
    system(command.str().c_str());

    std::ostringstream result;
    std::ifstream infile("/tmp/addr2line_output.txt");
    std::string line;
    if (std::getline(infile, line)) {
        result << "Resolved Address: " << line << std::endl;
    } else {
        result << "Failed to read addr2line output" << std::endl;
    }
    return result.str();
}


void ForkEBPF::handleOpcodeInvocation(S2EExecutionState *state, uint64_t guestDataPtr, uint64_t guestDataSize)
{
    S2E_FORKEBPF_COMMAND command;

    if (guestDataSize != sizeof(command)) {
        getWarningsStream(state) << "mismatched S2E_FORKEBPF_COMMAND size\n";
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
