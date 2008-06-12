/**
 * Get the config values from the user's musync.conf and import it to 
 * MainOptions so the corresponding check boxes gets checked.
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
class ExportMusync extends SubProcess
{
    private MainFrame frame;

    /**
     * Constructor.
     */
    public ExportMusync(String[] commands, MainFrame frame)
    {
        super(commands);
        this.frame = frame;
    }

    /**
     * Calls the export parser and then imports the config values to 
     * MainOptions.
     */
    public void read()
    {
        Commons.parseMusyncExport(getInputStreamReader());
        frame.center.opts.importKeys(Commons.getConfig());

        return;
    }

    /**
     * Needed by Subprocess, but we're not using it here.
     *
     * @param i It sure looks like an int.
     */
    public void end(int i)
    {
        return;
    }
}
