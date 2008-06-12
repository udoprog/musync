import java.lang.Thread;

/**
 * Run xterm as a subprocess.
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
class RunXtermWMusync extends SubProcess
{
    /**
     * Constructor send commands to subprocess.
     */
    public RunXtermWMusync(String[] commands)
    {
        super(commands);
    }

    /**
     * Needed for SubProcess, but we're not using it.
     */
    public void read() {
        return;
    };

    /**
     * What to do when done.
     *
     * @param exit The exit state from musync.
     */
    public void end(int exit)
    {
        System.out.println("exit value of musync: " + exit);

        return;
    }
}
