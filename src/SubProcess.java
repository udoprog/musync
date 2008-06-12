import java.lang.Thread;
import java.lang.Runtime;
import java.lang.Process;
import java.io.DataInputStream;
import java.io.InputStreamReader;
import java.io.DataOutputStream;
import java.io.OutputStreamWriter;

/**
 * Handles all the subprocesses.
 *
 * Copyright: John-John Tedro, Oscar Eriksson (2008)
 *
 *   This file is part of musync-swing.
 *
 *   musync-swing is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   musync-swing is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with musync-swing.  If not, see <http://www.gnu.org/licenses/>.
 */
abstract class SubProcess extends Thread
{
    protected InputStreamReader ifstream;
    protected OutputStreamWriter ofstream;
    private String[] commands;     // Commands to be executed.
    private Process p;             // Pointer to the process.
    private DataInputStream is;    // Data input steam (low-level).
    private DataOutputStream os;   // Data output stream (low-level).
    private boolean isInt = false; // iFlags weither process has been interrupted or not.
    private SPWriter writer;

    /**
     * Constructor taking arguments, when inheriting make certain to call 'super' properly.
     */
    public SubProcess(String[] commands)
    {
        this.commands = commands;
    }

    /**
     * Method 'run' inherited from Thread.
     * We create the relevant I/O-streams so we can easily communicate with subprocesses.
     */
    public void run()
    {
        Runtime r = Runtime.getRuntime();        
        try {
            p = r.exec(commands);
            is = new DataInputStream(p.getInputStream());
            ifstream = new InputStreamReader(is);
            os = new DataOutputStream(p.getOutputStream());
            ofstream = new OutputStreamWriter(os);
        } catch(java.io.IOException e) {
            //FIXME: what to do here?
        }

        // Fire up the thread meant to write to the process.
        if (writer != null) {
            writer.setOutputStreamWriter(ofstream);
            writer.start();
        }
        // Read all the process has to say.
        this.read();
        try {
            p.waitFor();
        } catch(java.lang.InterruptedException e) {
            Commons.epopup(e.toString());
        } finally {
            this.end(p.exitValue());
        }
    }

    /**
     * Return input stream (help method).
     *
     * @return InputStreamReader ifstream relevant to the process.
     */
    public InputStreamReader getInputStreamReader()
    {
        return ifstream;
    }

    /**
     * Return output stream (help method).
     *
     * @return OutputStreamWriter ofstream relevant to the process.
     */
    public OutputStreamWriter getOutputStreamWriter()
    {
        return ofstream;
    }

    /**
     * Set writer to a process.
     *
     * @param writer The writer.
     */
    public void setWriter(SPWriter writer)
    {
        this.writer = writer;
    }

    /**
     * Tell a subprocess that it has to close.
     */
    public void kill()
    {
        p.destroy();
        if (this.writer != null)
            this.writer.interrupt();
        isInt = true;
    }

    /**
     * Check in a subprocess if we have to close.
     *
     * @return True if is interupted, false otherwise.
     */
    public boolean isInterrupted()
    {
        return isInt;
    }
    
    /**
     * abstract method that will be called when process has been opened.
     */
    abstract public void read();
    abstract public void end(int ret);
}

/**
 * A help class to inherit when it is wanted to write to a process.
 */
abstract class SPWriter extends Thread
{
    OutputStreamWriter ofstream;
    
    public void setOutputStreamWriter(OutputStreamWriter ofstream)
    {
        this.ofstream = ofstream;
    }

    abstract public void run();
}
